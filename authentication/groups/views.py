from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMessage
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.views import View

from .forms import GroupForm, GroupFormCreate, InviteForm, PermissionForm
from .models import Invitation

STUDENT_GROUP_ALIASES = {"student", "students", "estudiante", "estudiantes"}
FACILITATOR_GROUP_ALIASES = {"facilitador", "facilitadores"}
ROLE_GROUPS = ("customers", "estudiantes", "Facilitadores", "tecnicos")


def _is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def _is_tecnico(user):
    return user.is_authenticated and user.groups.filter(name='tecnicos').exists()

def _can_invite(user):
    return _is_staff(user) or _is_tecnico(user)


def _normalize_student_membership(user):
    names = set(user.groups.values_list('name', flat=True))
    lowered = {name.lower() for name in names}
    if not lowered.intersection(STUDENT_GROUP_ALIASES):
        return

    canonical, _ = Group.objects.get_or_create(name='estudiantes')
    user.groups.add(canonical)

    for name in names:
        if name.lower() in STUDENT_GROUP_ALIASES and name != 'estudiantes':
            legacy = Group.objects.filter(name=name).first()
            if legacy:
                user.groups.remove(legacy)


def _normalize_facilitator_membership(user):
    names = set(user.groups.values_list('name', flat=True))
    lowered = {name.lower() for name in names}
    if not lowered.intersection(FACILITATOR_GROUP_ALIASES):
        return

    canonical, _ = Group.objects.get_or_create(name='Facilitadores')
    user.groups.add(canonical)

    for name in names:
        if name.lower() in FACILITATOR_GROUP_ALIASES and name != 'Facilitadores':
            legacy = Group.objects.filter(name=name).first()
            if legacy:
                user.groups.remove(legacy)

def _set_user_type(user, selected_type: str):
    selected_type = (selected_type or "").strip().lower()
    valid_types = {"customer", "estudiante", "facilitador", "tecnico", "staff", "superuser"}
    if selected_type not in valid_types:
        raise ValueError("Tipo de usuario invalido.")

    for group_name in ROLE_GROUPS:
        g = Group.objects.filter(name=group_name).first()
        if g:
            user.groups.remove(g)

    user.is_staff = False
    user.is_superuser = False

    if selected_type == "customer":
        g, _ = Group.objects.get_or_create(name="customers")
        user.groups.add(g)
    elif selected_type == "estudiante":
        g, _ = Group.objects.get_or_create(name="estudiantes")
        user.groups.add(g)
    elif selected_type == "facilitador":
        g, _ = Group.objects.get_or_create(name="Facilitadores")
        user.groups.add(g)
    elif selected_type == "tecnico":
        g, _ = Group.objects.get_or_create(name="tecnicos")
        user.groups.add(g)
    elif selected_type == "staff":
        user.is_staff = True
    elif selected_type == "superuser":
        user.is_staff = True
        user.is_superuser = True

    user.save(update_fields=["is_staff", "is_superuser"])



@user_passes_test(_is_staff)
def add_and_remove_group_to_user(request, user_id):
    if request.method == "POST":
        action = request.POST.get('action')
        group_ids = request.POST.getlist('group')
        user = User.objects.get(pk=user_id)
        if action == 'add':
            # Lógica para agregar grupos al usuario
            user.groups.add(*group_ids)
            _normalize_student_membership(user)
            _normalize_facilitator_membership(user)
        elif action == 'remove':
            # Lógica para eliminar grupos del usuario
            groups_to_remove = Group.objects.filter(id__in=group_ids)
            user.groups.remove(*groups_to_remove)
    return redirect ('user_list')

@user_passes_test(_is_staff)
def update_user_type(request, user_id):
    if request.method != "POST":
        return redirect("user_list")

    user = get_object_or_404(User, pk=user_id)
    selected_type = request.POST.get("user_type", "")

    if user.id == request.user.id and selected_type in {"customer", "estudiante", "facilitador", "tecnico"}:
        messages.error(request, "No puedes quitarte tus propios permisos administrativos desde aqui.")
        return redirect("user_list")

    try:
        _set_user_type(user, selected_type)
        messages.success(request, f"Tipo de usuario actualizado para {user.username}.")
    except ValueError:
        messages.error(request, "Tipo de usuario invalido.")
    except Exception:
        messages.error(request, "No se pudo actualizar el tipo de usuario.")

    return redirect("user_list")


@user_passes_test(_is_staff)
def bulk_update_user_type(request):
    if request.method != "POST":
        return redirect("user_list")

    selected_type = request.POST.get("user_type", "")
    raw_ids = (request.POST.get("user_ids_csv") or "").strip()

    if not raw_ids:
        messages.error(request, "Debes seleccionar al menos un usuario.")
        return redirect("user_list")

    try:
        user_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]
    except Exception:
        messages.error(request, "Lista de usuarios invalida.")
        return redirect("user_list")

    if not user_ids:
        messages.error(request, "Debes seleccionar al menos un usuario.")
        return redirect("user_list")

    updated = 0
    skipped = 0

    for user in User.objects.filter(id__in=user_ids):
        if user.id == request.user.id and selected_type in {"customer", "estudiante", "facilitador", "tecnico"}:
            skipped += 1
            continue
        try:
            _set_user_type(user, selected_type)
            updated += 1
        except Exception:
            skipped += 1

    if updated:
        messages.success(request, f"Tipo actualizado en {updated} usuario(s).")
    if skipped:
        messages.warning(request, f"{skipped} usuario(s) no se pudieron actualizar.")

    return redirect("user_list")


@user_passes_test(lambda u: u.is_authenticated and u.is_superuser)
def delete_user(request, user_id):
    if request.method != "POST":
        return redirect("user_list")

    target = get_object_or_404(User, pk=user_id)
    if target.id == request.user.id:
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("user_list")

    username = target.username
    target.delete()
    messages.success(request, f"Usuario '{username}' eliminado correctamente.")
    return redirect("user_list")

@user_passes_test(_is_staff)
def add_and_remove_permission_to_groups(request, group_id):
    if request.method == "POST":
        action = request.POST.get('action')
        Permission_ids = request.POST.getlist('permissions')
        group = Group.objects.get(pk=group_id)
        if action == 'add':
            # Lógica para agregar grupos al usuario
            group.permissions.add(*Permission_ids)
        elif action == 'remove':
            # Lógica para eliminar grupos del usuario
            group.permissions.remove(*Permission_ids)
    return redirect ('group_list')

@user_passes_test(_is_staff)
def group_list(request):
    groups = Group.objects.all()
    form_create_group = GroupFormCreate()
    form_add_permission = PermissionForm()
    
    context = {
        'groups': groups,
        'form_0': form_create_group,
        'form_1': form_add_permission,
    }
    return render(request, 'group_list.html', context)

@user_passes_test(_is_staff)
def group_create(request):
    if request.method == 'POST':
        form = GroupFormCreate(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')  # Redirigir a la lista de grupos después de la creación
    
    return redirect('group_list')

@user_passes_test(_is_staff)
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    
    if request.method == 'POST':
        form = GroupFormCreate(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')  # Redirigir a la lista de grupos después de la actualización
    else:
        form = GroupFormCreate(instance=group)
    
    return render(request, 'group_form.html', {'form': form, 'group': group, 'title': 'Editar Grupo'})

@user_passes_test(_is_staff)
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        try:
            group.delete()
            messages.success(request, "Grupo eliminado correctamente.")
        except ProtectedError:
            invites_count = group.invitations.count()
            messages.error(
                request,
                f"No se puede eliminar el grupo '{group.name}' porque tiene {invites_count} invitacion(es) asociadas."
            )
        return redirect('group_list')
    return render(request, 'group_confirm_delete.html', {'group': group})

@user_passes_test(_is_staff)
def user_list(request):
    users = User.objects.all().prefetch_related('groups')
    all_groups = Group.objects.all().order_by('name')
    for user in users:
        user.is_customer = user.groups.filter(name__iexact='customers').exists()
        user.is_student = user.groups.filter(name__iexact='estudiantes').exists()
        user.is_facilitador = user.groups.filter(name__iexact='Facilitadores').exists()
        user.is_tecnico = user.groups.filter(name__iexact='tecnicos').exists()
        role_hits = sum(
            int(flag) for flag in [
                user.is_customer,
                user.is_student,
                user.is_facilitador,
                user.is_tecnico,
            ]
        )

        if user.is_superuser:
            user.current_user_type = "superuser"
        elif user.is_staff:
            user.current_user_type = "staff"
        elif user.is_tecnico:
            user.current_user_type = "tecnico"
        elif user.is_facilitador:
            user.current_user_type = "facilitador"
        elif user.is_student:
            user.current_user_type = "estudiante"
        elif user.is_customer:
            user.current_user_type = "customer"
        else:
            user.current_user_type = ""

        user.has_mixed_roles = role_hits > 1 or ((user.is_staff or user.is_superuser) and role_hits > 0)
    return render(request, 'user_list.html', {'users': users, 'all_groups': all_groups})

class InviteFriendView(View):
    form_class = InviteForm
    template_name = 'invite_friend.html'

    def get(self, request):
        if not _can_invite(request.user):
            return redirect('login')
        if _is_tecnico(request.user) and not _is_staff(request.user):
            allowed_groups = Group.objects.filter(Q(name__iexact='Facilitadores') | Q(name__iexact='estudiantes_becados'))
        else:
            allowed_groups = Group.objects.all()
        initial = {}
        group_param = (request.GET.get('group') or '').strip()
        if group_param:
            try:
                g = allowed_groups.get(name__iexact=group_param)
                initial['group'] = g.id
            except Group.DoesNotExist:
                pass
        else:
            try:
                g = allowed_groups.get(name__iexact="estudiantes_becados")
                initial['group'] = g.id
            except Group.DoesNotExist:
                pass
        form = self.form_class(initial=initial, group_queryset=allowed_groups)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not _can_invite(request.user):
            return redirect('login')
        if _is_tecnico(request.user) and not _is_staff(request.user):
            allowed_groups = Group.objects.filter(Q(name__iexact='Facilitadores') | Q(name__iexact='estudiantes_becados'))
        else:
            allowed_groups = Group.objects.all()
        form = self.form_class(request.POST, group_queryset=allowed_groups)
        if form.is_valid():
            email = form.cleaned_data['email']
            group = form.cleaned_data['group']

            expires_at = timezone.now() + timedelta(days=getattr(settings, 'INVITATION_EXPIRE_DAYS', 7))
            invitation = Invitation.objects.create(
                email=email,
                group=group,
                created_by=request.user,
                expires_at=expires_at,
            )

            invite_url = request.build_absolute_uri(
                reverse('accept_invite', kwargs={'token': invitation.token})
            )

            subject = "¡Te han invitado a unirte a LivingBetterCC!"
            message_text = (
                "Hola,\n\n"
                f"Has sido invitado(a) a unirte al grupo '{group.name}'.\n\n"
                "Para aceptar la invitación, abre este enlace:\n\n"
                f"{invite_url}\n\n"
                "Si no solicitaste esto, puedes ignorar este correo."
            )

            EmailMessage(
                subject=subject,
                body=message_text,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                to=[email],
            ).send(fail_silently=False)

            messages.success(request, 'Tu invitación se ha enviado exitosamente.')
            return redirect('invite_success')
        
        return render(request, self.template_name, {'form': form})

def _safe_login_url() -> str:
    # Try common login route names, then fall back to settings.LOGIN_URL or a default path
    for name in ('authentication:login', 'account_login', 'login'):
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return getattr(settings, 'LOGIN_URL', '/accounts/login/')

def accept_invite(request, token):
    invitation = get_object_or_404(Invitation.objects.select_related('group'), token=token)

    if invitation.is_used() or invitation.is_expired():
        messages.error(request, 'Esta invitación ya fue usada o expiró.')
        return redirect(_safe_login_url())

    if not request.user.is_authenticated:
        request.session['pending_invitation_token'] = str(invitation.token)
        request.session['post_register_role'] = invitation.group.name
        request.session['invited_email'] = invitation.email
        messages.info(request, 'Inicia sesión o regístrate para aceptar la invitación.')
        return redirect(_safe_login_url())

    invited_email = (invitation.email or "").strip().lower()
    user_email = (request.user.email or "").strip().lower()
    if invited_email and user_email and invited_email != user_email:
        messages.error(request, 'Esta invitación no corresponde a tu correo.')
        return redirect('dashboard')

    # Authenticated users can auto-accept invitations to 'estudiantes_becados',
    # even if they already belong to other groups.
    if invitation.group.name.lower() == 'estudiantes_becados':
        request.user.groups.add(invitation.group)
        invitation.mark_used(request.user)
        messages.success(request, "Invitación aceptada. Ahora tienes acceso a 'estudiantes_becados'.")
        return redirect('dashboard')

    messages.info(request, 'Esta invitación requiere registro nuevo. Si ya tienes cuenta, pide al admin que te agregue al grupo.')
    return redirect('dashboard')

def invite_success(request):
    """Vista que muestra un mensaje de éxito después de enviar la invitación."""
    return render(request, 'invite_success.html', {'message': 'Tu invitación se ha enviado exitosamente.'})

