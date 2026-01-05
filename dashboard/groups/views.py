from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from django.views import View

from .forms import GroupForm, GroupFormCreate, InviteForm, PermissionForm
from .models import Invitation


def _is_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)



@user_passes_test(_is_staff)
def add_and_remove_group_to_user(request, user_id):
    if request.method == "POST":
        action = request.POST.get('action')
        group_ids = request.POST.getlist('group')
        user = User.objects.get(pk=user_id)
        if action == 'add':
            # Lógica para agregar grupos al usuario
            user.groups.add(*group_ids)
        elif action == 'remove':
            # Lógica para eliminar grupos del usuario
            groups_to_remove = Group.objects.filter(id__in=group_ids)
            user.groups.remove(*groups_to_remove)
    return redirect ('user_list')

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
    
    form.fields['name'].widget.attrs.update

@user_passes_test(_is_staff)
def user_list(request):
    users = User.objects.all().prefetch_related('groups')
    for user in users:
        user.is_customer = user.groups.filter(name='customers').exists()
        user.is_student = user.groups.filter(name__in=['student', 'students']).exists()
    return render(request, 'user_list.html', {'users': users})

class InviteFriendView(View):
    form_class = InviteForm
    template_name = 'invite_friend.html'

    def get(self, request):
        if not _is_staff(request.user):
            return redirect('login')
        initial = {}
        group_param = (request.GET.get('group') or '').strip()
        if group_param:
            try:
                from django.contrib.auth.models import Group
                g = Group.objects.get(name__iexact=group_param)
                initial['group'] = g.id
            except Group.DoesNotExist:
                pass
        form = self.form_class(initial=initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not _is_staff(request.user):
            return redirect('login')
        form = self.form_class(request.POST)
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

    if invitation.email and request.user.email and invitation.email.strip().lower() != request.user.email.strip().lower():
        messages.error(request, 'Esta invitación no corresponde a tu correo.')
        return redirect('dashboard')

    request.user.groups.add(invitation.group)
    invitation.mark_used(request.user)
    messages.success(request, f"Invitación aceptada. Ahora perteneces al grupo '{invitation.group.name}'.")
    return redirect('dashboard')

def invite_success(request):
    """Vista que muestra un mensaje de éxito después de enviar la invitación."""
    return render(request, 'invite_success.html', {'message': 'Tu invitación se ha enviado exitosamente.'})

