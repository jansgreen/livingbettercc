from .forms import FacilitadorRegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from classroom.enrollments.models import Enrollment, LessonCompletion

from .forms import BootstrapUserCreationForm, ProfileForm, CustomerForm, AddressForm, DirectivesForm
from authentication.models.profiles import Profiles 
from authentication.models.customers import Customers
from authentication.models.directives import Directives
from authentication.models.address import Address
from authentication.models.students import Students

from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_backends
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



# identifico si el usuario es studiante, customer o staff ..

def facilitador_register_view(request):
    next_url = request.GET.get('next', None)
    if request.method == 'POST':
        form = FacilitadorRegistrationForm(request.POST)
        if form.is_valid():
            user, distrito, address = form.save()
            # Asignar grupo facilitador
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='facilitador')
            user.groups.add(group)
            # Autenticar usuario
            from django.contrib.auth import login, get_backends
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            # Redirigir al formulario original
            if next_url:
                return redirect(next_url)
            else:
                from django.urls import reverse
                return redirect(reverse('dashboard'))
        else:
            messages.error(request, "Por favor verifica los datos del formulario.")
    else:
        form = FacilitadorRegistrationForm()
    return render(request, 'authentication/facilitador_register.html', {'form': form})


def tecnico_register_view(request):
    """
    Registro para técnicos. Igual que el registro de facilitador pero asigna
    al grupo 'tecnico'. Los técnicos pueden revisar qué formularios completaron
    los facilitadores (acceso de solo lectura).
    """
    next_url = request.GET.get('next', None)
    if request.method == 'POST':
        form = FacilitadorRegistrationForm(request.POST)
        if form.is_valid():
            user, distrito, address = form.save()
            # Asignar grupo tecnico
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='tecnico')
            user.groups.add(group)
            # Autenticar usuario
            from django.contrib.auth import login, get_backends
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            # Redirigir al listado de facilitadores para revisar formularios
            if next_url:
                return redirect(next_url)
            else:
                from django.urls import reverse
                return redirect(reverse('formbuilder:facilitador_list_view'))
        else:
            messages.error(request, "Por favor verifica los datos del formulario.")
    else:
        form = FacilitadorRegistrationForm()
    return render(request, 'authentication/facilitador_register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
    else:
        form = AuthenticationForm()

    # Add 'form-control' class to all fields in the form
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    return render(request, 'authentication/login.html', {'form': form})

def register_view(request):
    
    if request.method == 'POST':
        form = BootstrapUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Recuperar datos temporales de la sesión
            role = request.session.get('post_register_role', None)
            item_id = request.session.get('selected_item', None)
            student_mode = request.session.get('student_register_mode', None)
            # 1. Asignar grupo (si role viene de la sesión)
            if role:
                group, created = Group.objects.get_or_create(name=role)
                user.groups.add(group)

            # Si venía para tomar un curso y registrarse como estudiante
            if role == 'student' and item_id:
                Enrollment.objects.get_or_create(user=user, course_id=item_id)

            # Estudiante que viene por Distrito Educativo
            elif role == 'student' and student_mode == 'district':
                # Limpiamos solo esa bandera
                request.session.pop('student_register_mode', None)
                messages.info(request, "Bienvenido(a). Completa el formulario del Distrito Educativo.")
                return redirect('students:student_by_district')

            # Si venía como cliente comprando algo
            elif role == 'customer' and item_id:
                cart = request.session.get('cart', [])
                request.session.pop('cart', None)

            # Si el rol es facilitador (docente, staff educativo)
            elif role == 'facilitador' and item_id:
                messages.info(request, "Listo ya te has registrado, ahora por favor completa el formulario.")
                return redirect('formbuilder:form_detail', item_id)

            # 3. Limpiar variables temporales de la sesión
            request.session.pop('post_register_role', None)
            request.session.pop('selected_item', None) 

            messages.success(request, 'Tu cuenta ha sido creada con éxito.')
            return redirect('dashboard')

        else:
            messages.error(request, f'Por favor verifica los datos del formulario: {form.errors}')
    else:
        form = BootstrapUserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')  # Redirect to login after logout

def prepare_register(request, pk, role):
    if request.user.is_authenticated:
        group = Group.objects.get(name=role)
        request.user.groups.add(group)
        return redirect('dashboard')

    request.session['post_register_role'] = role
    request.session['selected_item'] = pk
    return redirect('register')

def profile_create_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Set the user to the currently logged-in user
            profile.old_cart = ''  # Initialize old_cart or set as needed
            if not Address.objects.filter(user=request.user, address_type='Residencial').exists():
                address, created = Address.objects.get_or_create(user=request.user, address_type='Residencial')
                profile.direccion = address
                profile.save()
                if created:
                    return redirect('address_create', address_type='Residencial')
            if not profile.direccion:
                return redirect('address_create', address_type='Residencial')  # Redirect to address creation if direccion is not set
            return redirect('profile_list')  # Redirect to profile list after creation
    else:
        form = ProfileForm()
    return render(request, 'authentication/profile_create.html', {'form': form})

def profile_list_view(request):
    object_list = User.objects.all()
    context = {'object_list': object_list}
    return render(request, 'authentication/profile_list.html', context)

def profile_update_view(request, pk):
    profile = get_object_or_404(Profiles, pk=pk)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_list')  # Redirect to profile list after update
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'authentication/profile_update.html', {'form': form})

def profile_delete_view(request, pk):
    profile = get_object_or_404(Profiles, pk=pk)
    if request.method == 'POST':
        profile.delete()
        return redirect('profile_list')  # Redirect to profile list after deletion
    return render(request, 'authentication/profile_delete.html', {'profile': profile})

def profile_view(request):
    profile = Profiles.objects.filter(user=request.user)
    beca_status = None
    from classroom.enrollments.models import BecaApplication
    beca_app = BecaApplication.objects.filter(user=request.user).order_by('-fecha_aplicacion').first()
    if beca_app:
        beca_status = beca_app.estado
    context = {
        'profile': profile,
        'beca_status': beca_status,
    }
    return render(request, 'authentication/profile_detail.html', context)


@csrf_exempt
def customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Check if the user already exists
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe. Por favor, elige otro nombre de usuario.')
                return redirect('login')  # Redirect to the same page or another appropriate page
            
            # Save the user
            user = form.save(commit=False)
            user.save()

            # Save the address
            Address.objects.create(
                user=user,
                street=request.POST.get('street'),
                neighborhood=request.POST.get('neighborhood'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                zip_code=request.POST.get('zip_code'),
            )

            # Authenticate and log in the user
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            auth_login(request, user)
            return redirect('checkout_list')  # Redirect to the next stage
        else:
            messages.error(request, f'{form.errors} Error al crear el cliente. Por favor, corrige los errores.')
            return redirect('shop:checkout')  # Redirect to the next stage
    else:
        form = CustomerForm()
    return render(request, 'customers/customers.html', {'form': form})

def customer_list_view(request):
    customers = Customers.objects.all()
    return render(request, 'customers/customer_list.html', {'customers': customers})

def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect to customer list after creation
    else:
        form = CustomerForm()
    return render(request, 'customers/customer_create.html', {'form': form})

def customer_update_view(request, pk):
    customer = get_object_or_404(Customers, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # Redirect to customer list after update
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/customer_update.html', {'form': form})

def customer_delete_view(request, pk):
    customer = get_object_or_404(Customers, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')  # Redirect to customer list after deletion
    return render(request, 'customers/customer_delete.html', {'customer': customer})

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'authentication/address_list.html', {'addresses': addresses})

@login_required
def address_detail(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    return render(request, 'authentication/address_detail.html', {'address': address})

@login_required
def address_create(request, address_type):
    """
    Crea o actualiza una dirección del tipo especificado para el usuario actual.
    Si ya existe una dirección de ese tipo, la actualiza.
    """
    # Obtener dirección existente si existe
    address_instance = Address.objects.filter(user=request.user, address_type=address_type).first()
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.address_type = address_type
            address.save()
            
            messages.success(request, f'Dirección {address.get_address_type_display()} guardada exitosamente.')
            
            # Redirigir según el contexto (puede personalizarse)
            next_url = request.GET.get('next', 'courses:course_list')
            return redirect(next_url)
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AddressForm(instance=address_instance)
    
    context = {
        'form': form,
        'address_type': address_type,
        'address_type_display': dict(Address.a_type).get(address_type, address_type),
    }
    return render(request, 'direccion.html', context)


@login_required
def address_update(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'authentication/address_form.html', {'form': form})

@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('address_list')
    return render(request, 'authentication/address_confirm_delete.html', {'address': address})

def DirectivesCreate(request):

    directives_form = DirectivesForm(user=request.user)

    if request.method == 'POST':
        directives_form = DirectivesForm(request.POST, user=request.user)

        if directives_form.is_valid():
            # Save the directives
            directives = directives_form.save(commit=False)
            directives.user = request.user
            directives.save()

            messages.success(request, 'Directives and biography created successfully.')
            return redirect('quienes_somos')

    return render(request, 'directivas/create_directives.html', {
        'directives_form': directives_form,
    })


# CRUD de la Directiva


@login_required
def directives_list(request):
    directives = Directives.objects.all()
    return render(request, "directivas/directives_list.html", {"directives": directives})


@login_required
def directives_create(request):
    if request.method == "POST":
        form = DirectivesForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil se ha creado con exitos')
            return redirect("directives_list")
        else:
            messages.error(request, f'{form.errors} Corrije el siguiente error')
    else:
        form = DirectivesForm()
    return render(request, "directivas/directives_form.html", {"form": form, "title": "Crear Directivo"})


@login_required
def directives_update(request, pk):
    directive = get_object_or_404(Directives, pk=pk)
    if request.method == "POST":
        form = DirectivesForm(request.POST, request.FILES, instance=directive)
        if form.is_valid():
            form.save()
            return redirect("directives_list")
    else:
        form = DirectivesForm(instance=directive)
    return render(request, "directivas/directives_form.html", {"form": form, "title": "Editar Directivo"})


@login_required
def directives_delete(request, pk):
    directive = get_object_or_404(Directives, pk=pk)
    if request.method == "POST":
        directive.delete()
        return redirect("directives_list")
    return render(request, "directivas/directives_confirm_delete.html", {"directive": directive})
