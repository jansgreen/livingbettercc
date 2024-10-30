from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group, User
from .forms import GroupForm, PermissionForm, GroupFormCreate, InviteForm
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.contrib.auth.decorators import user_passes_test
from django.views import View
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages



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

def group_create(request):
    if request.method == 'POST':
        form = GroupFormCreate(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_list')  # Redirigir a la lista de grupos después de la creación
    
    return redirect('group_list')

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

def user_list(request):
    users = User.objects.all()
    form = GroupForm()
    return render(request, 'user_list.html', {'users': users, 'form': form})

class InviteFriendView(View):
    form_class = InviteForm
    template_name = 'invite_friend.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            group = form.cleaned_data['group']

            # Generar el token para el enlace único
            token = default_token_generator.make_token(User(email=email))
            uid = urlsafe_base64_encode(force_bytes(email))

            # Construir el enlace de invitación
            current_site = get_current_site(request)
            invite_url = reverse('accept_invite', kwargs={'uidb64': uid, 'token': token, 'group_id': group.id})
            full_invite_url = f"http://{current_site.domain}{invite_url}"

            # Preparar y enviar el email en texto plano
            subject = "¡Te han invitado a unirte a nuestro sitio!"
            message_text = (
                f"Hola,\n\n"
                f"Has sido invitado a unirte al grupo '{group.name}' en nuestro sitio.\n"
                f"Para aceptar la invitación, haz clic en el siguiente enlace:\n\n"
                f"{full_invite_url}\n\n"
                f"Si no puedes hacer clic en el enlace, cópialo y pégalo en tu navegador."
            )
            email_message = EmailMessage(
                subject=subject,
                body=message_text,
                from_email=settings.EMAIL_HOST_USER,
                to=[email]
            )
            email_message.send(fail_silently=False)

            messages.success(request, 'Tu invitación se ha enviado exitosamente.')
            return redirect('invite_success')
        
        return render(request, self.template_name, {'form': form})


@login_required
def accept_invite(request, uidb64, token, group_id):
    # Obtener el grupo
    group = get_object_or_404(Group, id=group_id)

    # Si el token es válido y el usuario está autenticado
    if default_token_generator.check_token(request.user, token):
        request.user.groups.add(group)  # Asigna el grupo al usuario
        return redirect('success_page')  # Redirige a la página de éxito

    # Redirige a login si el token no es válido o el usuario no está autenticado
    return redirect('login')

def invite_success(request):
    """Vista que muestra un mensaje de éxito después de enviar la invitación."""
    return render(request, 'invite_success.html', {'message': 'Tu invitación se ha enviado exitosamente.'})

