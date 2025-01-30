from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, LoginForm, Profileforms, BiographyForm, DireccionForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Biography, Profile, Direccion
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from django.http import HttpResponse


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('shop')  # Redirigir a la página principal
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
    try:
        # Obtener el perfil del usuario si existe
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None  # Si no existe, dejamos profile como None

    if request.method == 'POST':
        # Si el perfil existe, se pasa como instancia al formulario; de lo contrario, se crea uno nuevo
        forms = Profileforms(request.POST, request.FILES, instance=profile, user=request.user)
        if forms.is_valid():
            user = request.user
            user.first_name = forms.cleaned_data.get('first_name', user.first_name)
            user.last_name = forms.cleaned_data.get('last_name', user.last_name)
            user.save()
            profile = forms.save(commit=False)
            profile.user = request.user  # Aseguramos que el perfil esté relacionado con el usuario
            profile.save()  # Guarda y retorna la instancia
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('direccion')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        # Si no es POST, inicializa el formulario con la instancia existente o vacío
        forms = Profileforms(instance=profile, user=request.user)

    # Renderizar el formulario en el contexto
    context = {
        'profile': profile,
        'forms': forms}
    return render(request, 'Profile.html', context)

def direccion(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            # Guardar o actualizar la dirección
            direccion = form.save()
            profile.direccion = direccion  # Asignar la dirección al perfil
            profile.save()  # Guardar el perfil con la dirección asignada

            messages.success(request, 'Dirección asignada exitosamente.')
            return redirect('ProfileFunction')  # Redirigir al perfil del usuario
    else:
        form = DireccionForm(instance=profile.direccion)

    return render(request, 'direccion.html', {'form': form})

def actualizar_direccion(request, direccion_id):
    profile = Profile.objects.filter(direccion=direccion_id)

    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar los cambios en la dirección
            messages.success(request, 'Dirección actualizada exitosamente.')
            return redirect('profileFunction')
    form = DireccionForm()
    return render(request, 'direccion.html', {'form': form, 'profile': profile})

def eliminar_direccion(request, direccion_id):
    direccion = get_object_or_404(Direccion, id=direccion_id)
    direccion.delete()
    messages.success(request, 'Dirección eliminada exitosamente.')
    return redirect('ProfileFunction')  # Redirige al perfil del usuario o a la lista de direcciones

def edit_profile(request):
    # Obtén el perfil del usuario actual o redirige si no existe
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "No se encontró el perfil del usuario.")
        return redirect('some_error_page')

    forms_Address = DireccionForm()
    forms = Profileforms(instance=profile)  # Pasar el perfil actual para inicializar el formulario

    if request.method == "POST":
        # Procesar datos de los formularios
        forms = Profileforms(request.POST, request.FILES, instance=profile, user=request.user)
        datas = request.POST
        files = request.FILES  # Archivos enviados, incluidas imágenes

        for action, info in datas.items():
            if info:  # Validar que la información no esté vacía
                if action in ['calle_y_casa', 'sector_o_barrio', 'provincia', 'municipio', 'zip']:
                    # Actualiza múltiples campos de dirección (asegúrate de tener un campo 'direccion')
                    if hasattr(profile, 'direccion'):
                        direccion = getattr(profile, 'direccion', None)
                        if direccion:  # Si la dirección existe
                            setattr(direccion, action, info)
                            direccion.save()
                        else:
                            messages.error(request, "No se encontró la dirección asociada al perfil.")
                            return redirect('some_error_page')
                else:
                    # Actualiza campos del perfil directamente
                    if hasattr(profile, action):
                        setattr(profile, action, info)

        # Procesar y guardar la imagen, si se subió
        print(files['imagen'])
        if 'imagen' in files:  # Suponiendo que el campo del formulario se llama 'image'
            profile.imagen = files['imagen']
            profile.save()

        # Mensaje de éxito
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('ProfileFunction')

    context = {
        'forms': forms,
        'forms_Address': forms_Address,
        'profile': profile,
    }
    return render(request, 'editProfile.html', context)

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
            return redirect('quienes_somos')  # Cambia esto a la URL a la que quieras redirigir después de guardar
    else:
        form = BiographyForm(instance=biography)

    return render(request, 'edit_biograph.html', {'form': form})

def leerBio(request, pk):
    managers = User.objects.filter(groups__name='manager').select_related('profile')
    managers = sorted(managers, key=lambda x: x.profile.roll != 'CEO')
    articles = Biography.objects.filter(user=pk)
    context={
        'articles':articles,
        'managers':managers,
    }
    return render(request, 'leer_bio.html', context)
