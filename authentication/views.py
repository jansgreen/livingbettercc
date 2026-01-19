from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from classroom.enrollments.models import Enrollment, LessonCompletion

from .forms import BootstrapUserCreationForm, ProfileForm, CustomerForm, DirectivesForm
from authentication.address.forms import AddressForm
from authentication.models.profiles import Profiles 
from authentication.models.customers import Customers
from authentication.models.directives import Directives
from authentication.address.models import Address
from authentication.models.students import Students

from formbuilder.forms import FacilitadorRegistrationForm

from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_backends
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from dashboard.groups.models import Invitation
from django.contrib.auth import login, get_backends
from django.urls import reverse
from django.shortcuts import redirect

def _dedupe_student_groups(user):
    """If both 'student' and 'students' are present, keep only 'students'."""
    if not user or not getattr(user, 'is_authenticated', False):
        return
    names = set(user.groups.values_list('name', flat=True))
    if 'student' in names and 'students' in names:
        try:
            user.groups.remove(Group.objects.get(name='student'))
        except Group.DoesNotExist:
            return

def _apply_pending_invitation(request, user):
    token = request.session.get('pending_invitation_token')
    if not token or not user or not user.is_authenticated:
        return False

    try:
        invitation = Invitation.objects.select_related('group').get(token=token)
    except Exception:
        request.session.pop('pending_invitation_token', None)
        request.session.pop('invited_email', None)
        return False

    if invitation.is_used() or invitation.is_expired():
        messages.error(request, 'La invitación ya fue usada o expiró.')
        request.session.pop('pending_invitation_token', None)
        request.session.pop('invited_email', None)
        return False

    invited_email = (request.session.get('invited_email') or invitation.email or '').strip().lower()
    user_email = (user.email or '').strip().lower()
    if invited_email and user_email and invited_email != user_email:
        messages.error(request, 'Esta invitación no corresponde a tu correo.')
        request.session.pop('pending_invitation_token', None)
        request.session.pop('invited_email', None)
        return False

    user.groups.add(invitation.group)
    invitation.mark_used(user)
    _dedupe_student_groups(user)

    if request.session.get('selected_item') is None and request.session.get('post_register_role') == invitation.group.name:
        request.session.pop('post_register_role', None)

    request.session.pop('pending_invitation_token', None)
    request.session.pop('invited_email', None)
    messages.success(request, 'Invitación aceptada correctamente.')
    return True

# identifico si el usuario es studiante, customer o staff ..

def facilitador_register_view(request):
    next_url = request.GET.get('next', None)
    if request.method == 'POST':
        form = FacilitadorRegistrationForm(request.POST)
        if form.is_valid():
            user, distrito, address = form.save()
            # Asignar grupo facilitador
            group, _ = Group.objects.get_or_create(name='facilitador')
            user.groups.add(group)
            # Autenticar usuario
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)
            # Redirigir al formulario original
            if next_url:
                return redirect(next_url)
            else:
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
    form = BootstrapUserCreationForm()
    if request.method == 'POST':
        form = BootstrapUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            invite_applied = _apply_pending_invitation(request, user)
            _dedupe_student_groups(user)
            # Reanudar intención: delegar al flujo de Classroom
            role = request.session.get('post_register_role')
            item_id = request.session.get('selected_item')
            if item_id:
                if role:
                    group, _ = Group.objects.get_or_create(name=role)
                    user.groups.add(group)
                request.session.pop('post_register_role', None)
                return redirect('courses:start_course_payment', pk=item_id)
            if invite_applied:
                return redirect('dashboard')
            return redirect('home')

    # Add 'form-control' class to all fields in the form
    for field in form.fields.values():
        field.widget.attrs.update({'class': 'form-control'})

    return render(request, 'authentication/login.html', {'form': form})

def register_view(request):
    
    if request.method == 'POST':
        form = BootstrapUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Autenticamos al usuario recién creado para mantener la sesión
            try:
                backend = get_backends()[0]
                user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
                auth_login(request, user)
            except Exception:
                # Si por alguna razón no podemos autenticar ahora, seguimos sin fallo
                pass

            # Recuperar datos temporales de la sesión
            role = request.session.get('post_register_role', None)
            item_id = request.session.get('selected_item', None)
            student_mode = request.session.get('student_register_mode', None)

            # Invitación pendiente (si existe)
            _apply_pending_invitation(request, user)
            # 1. Asignar grupo (si role viene de la sesión)
            if role:
                group, created = Group.objects.get_or_create(name=role)
                user.groups.add(group)

            _dedupe_student_groups(user)

            # Si venía para tomar un curso y registrarse como estudiante
            if role == 'student' and item_id:
                # No crear Enrollment aquí; delegar a Classroom
                request.session.pop('post_register_role', None)
                return redirect('courses:start_course_payment', pk=item_id)

            # Estudiante que viene por Distrito Educativo
            elif role == 'student' and student_mode == 'district':
                # Limpiamos solo esa bandera
                request.session.pop('student_register_mode', None)
                messages.info(request, "Bienvenido(a). Completa el formulario del Distrito Educativo.")
                return redirect('students:student_by_district')

            # Si venía como cliente comprando algo
            elif role == 'customer' and item_id:
                # Flujo de tienda no aplica a cursos
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
    return redirect('authentication:login')  # Redirect to login after logout

def prepare_register(request, pk, role): 
    # Solo guardar intención en sesión y asegurar grupo; no crear Enrollment aquí
    request.session['post_register_role'] = role
    request.session['selected_item'] = int(pk)

    if request.user.is_authenticated:
        # Asegurar grupo idempotente
        group, _ = Group.objects.get_or_create(name=role)
        request.user.groups.add(group)
        # Redirigir al flujo de Classroom para decidir Enrollment/estado/pago
        return redirect('courses:start_course_payment', pk=pk)

    # Usuario no autenticado: continuar con registro/login con next; luego reanudar desde sesión
    next_url = reverse('courses:start_course_payment', kwargs={'pk': pk})
    return redirect(f"{reverse('authentication:register')}?next={next_url}")

def profile_create_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Set the user to the currently logged-in user
            profile.old_cart = ''  # Initialize old_cart or set as needed
            profile.save()
            if not Address.objects.filter(user=request.user, address_type='residencial').exists():
                address, created = Address.objects.get_or_create(user=request.user, address_type='residencial')
                profile.direccion = address
                profile.save()
                if created:
                    # After creating initial residencial address record, direct user to complete details
                    addr_url = reverse('authentication:address:address_create', kwargs={'address_type': 'residencial', 'pk': request.user.id})
                    next_url = reverse('authentication:profile_list')
                    return redirect(f"{addr_url}?next={next_url}")
            if not profile.direccion:
                addr_url = reverse('authentication:address:address_create', kwargs={'address_type': 'residencial', 'pk': request.user.id})
                next_url = reverse('authentication:profile_list')
                return redirect(f"{addr_url}?next={next_url}")  # Redirect to address creation if direccion is not set
            return redirect('profile_list')  # Redirect to profile list after creation
        else:
            messages.error(request, f'{{form.errors}}, Por favor verifica los datos del formulario: {form.errors}')
    else:
        form = ProfileForm()
    return render(request, 'authentication/profile_create.html', {'form': form})

def profile_list_view(request):
    object_list = User.objects.all()
    context = {'object_list': object_list}
    return render(request, 'authentication/profile_list.html', context)

@login_required
def profile_view(request):
    profile = Profiles.objects.filter(user=request.user)
    beca_status = None
    from classroom.enrollments.models import BecaApplication
    beca_app = BecaApplication.objects.filter(user=request.user).order_by('-fecha_aplicacion').first()
    if beca_app:
        beca_status = beca_app.status
    context = {
        'profile': profile,
        'beca_status': beca_status,
    }
    return render(request, 'authentication/profile_detail.html', context)

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

@csrf_exempt
def customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            # Check if the user already exists
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe. Por favor, elige otro nombre de usuario.')
                return redirect('login')
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
            return redirect('shop:checkout')
    else:
        form = CustomerForm()
    return render(request, 'customers/customers.html', {'form': form})

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
# Address view aliases for legacy URL patterns
def address_list(request):
    return redirect('authentication:address:address_list')

def address_detail(request, pk):
    return redirect('authentication:address:address_detail', pk=pk)

def address_create(request, address_type, pk):
    return redirect('authentication:address:address_create', address_type=address_type, pk=pk)

def address_update(request, pk):
    return redirect('authentication:address:address_update', pk=pk)

def address_delete(request, pk):
    return redirect('authentication:address:address_delete', pk=pk)
