from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, Profileforms, Profile, BiographyForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Biography
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog')  # Redirigir a la página principal
        else:
            print(form.errors)
            messages.debug(request, f'{form.errors}')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def custom_login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            messages.info(request, f'{username} !ya te logeaste!')
            if user is not None:
                login(request, user)
                messages.info(request, f'{username} !ya te logeaste!')
                return redirect('home')  # Redirige a la página principal o a otra de tu elección
        else:
            # Si el formulario no es válido, seguirá mostrando los errores en el template
            return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def custom_logout_view(request):
    logout(request)
    return redirect('home')  # Redirige a 'home' o a la página que desees después 

def ProfileFunction(request):
    user = request.user
    
    # Verifica si el perfil ya existe, si no, crea uno nuevo
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = Profileforms(request.POST, request.FILES, instance=profile)
        user = request.user
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')

        if form.is_valid():
            form = form.save(commit=False)
            form.user = user
            form.provincia = request.POST.get('provincia')
            form.municipio = request.POST.get('municipios')
            form.codigo_postal = request.POST.get('zip')
            form.save()  # Guarda la instancia del perfil
            user.save()
            messages.success(request, f'{request.user} tu perfil ha sido guardado')
            return redirect('ProfileFunction')  # Cambia esto por tu URL de éxito
        else:
            messages.success(request, f'{form.errors} tu perfil ha sido guardado')
    form = Profileforms(instance=profile)  # Pasa la instancia existente si está en modo GET
    return render(request, 'profile.html', {'form': form, 'profile': profile})

def edit_profile(request):
    # Obtén el perfil del usuario actual o redirige si no existe
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == "POST":
        action = request.POST.get('action', '')
        # Mapeo de acciones a campos de perfil
        actions_map = {
            'edit_first_name': 'first_name',
            'edit_last_name': 'last_name',
            'edit_telefono': 'telefono',
            'edit_profesion': 'profesion',
            'edit_puesto': 'puesto',
            'edit_image': 'Foto de perfil',
            'edit_numero_identidad': 'numero_identidad',
            'edit_direccion': [
                'calle_y_casa', 
                'sector_o_barrio', 
                'provincia', 
                'municipio', 
                'zip',
            ]
        }

        # Actualizar el perfil basado en la acción
        if action in actions_map:

            if action == 'edit_direccion':
                # Actualiza múltiples campos para dirección
                profile.calle_y_casa = request.POST.get('calle_y_casa', profile.calle_y_casa)
                profile.sector_o_barrio = request.POST.get('sector_o_barrio', profile.sector_o_barrio)
                profile.provincia = request.POST.get('provincia', profile.provincia)
                profile.municipio = request.POST.get('municipio', profile.municipio)
                profile.codigo_postal = request.POST.get('zip', profile.codigo_postal)
            elif  action =='edit_first_name':
                user = request.user
                user.first_name = request.POST.get('firstname')
                user.save()
            elif  action =='edit_last_name':
                user = request.user
                user.last_name = request.POST.get('lastname')                
                user.save()

            else:
                # Actualiza un solo campo
                setattr(profile, actions_map[action], request.POST.get(actions_map[action], getattr(profile, actions_map[action])))

            # Guardar los cambios en el perfil
                profile.save()

            # Mensaje de éxito
            messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('ProfileFunction')
    
    else:
        print("not paso el metodo")

@login_required
def edit_biography(request):
    try:
        biography = Biography.objects.get(user=request.user)
    except Biography.DoesNotExist:
        biography = None

    if request.method == 'POST':
        form = BiographyForm(request.POST, instance=biography)
        if form.is_valid():
            biography = form.save(commit=False)
            biography.user = request.user
            biography.save()
            messages.success(request, f'{request.user} Tu Biografia se creo exitosamente!')
            return redirect('aboutUs')  # Cambia esto a la URL a la que quieras redirigir después de guardar
    else:
        form = BiographyForm(instance=biography)

    return render(request, 'edit_biograph.html', {'form': form})
