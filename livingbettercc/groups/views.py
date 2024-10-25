from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group, User
from .forms import GroupForm, PermissionForm, GroupFormCreate, InviteForm
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test

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

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from .forms import InviteForm

def invite_to_register(request):
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            group_name = form.cleaned_data['group'].name
            group = Group.objects.get(name=group_name)
           
            # Crear el enlace de registro con un token único (puedes mejorar esto con un sistema de tokens)
            register_url = f'http://tu_dominio.com/register/?email={email}&group={group}'
            
            # Crear el mensaje de invitación
            subject = 'Invitación para Registrarse'
            message = f'Has sido invitado a registrarte en nuestra plataforma y unirte al grupo "{group}". Por favor, sigue el enlace para registrarte: {register_url}'
            from_email = 'tu_email@gmail.com'
           
            # Enviar correo electrónico
            send_mail(subject, message, from_email, [email])
           
            return redirect('invite_to_register')
    else:
        form = InviteForm()
    
    groups = Group.objects.all()
    return render(request, 'invite_to_register.html', {'form': form, 'groups': groups})
