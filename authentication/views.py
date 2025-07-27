from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from authentication.models import address
from .forms import BootstrapUserCreationForm, ProfileForm, CustomerForm, AddressForm, DirectivesForm
from authentication.models.profiles import Profiles 
from authentication.models.customers import Customers
from authentication.models.directives import Directives
from authentication.models.address import Address

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import get_backends
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

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
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = BootstrapUserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')  # Redirect to login after logout

def profile_create_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile_list')  # Redirect to profile list after creation
    else:
        form = ProfileForm()
    return render(request, 'authentication/profile_create.html', {'form': form})

def profile_list_view(request):
    profiles = Profiles.objects.all()
    return render(request, 'authentication/profile_list.html', {'profiles': profiles})

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

def profile_view(request, pk):
    profile = get_object_or_404(Profiles, pk=pk)
    return render(request, 'authentication/profile_detail.html', {'profile': profile})

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
    if request.method == 'POST':
        form = AddressForm(request.POST)
        print(f"Form data: {request.POST}")  # Debugging line
        if form.is_valid():
            address_fields = {
                'user': request.user,
                'address_type': address_type,
                'street': request.POST.get('street'),
                'neighborhood': request.POST.get('neighborhood'),
                'city': request.POST.get('provincias'),
                'state': request.POST.get('municipios'),
                'zip_code': request.POST.get('codigo_postal'),
            }
            for key, value in form.cleaned_data.items():
                setattr(address, key, value)
            # Explicitly update fields that may be excluded from the form's Meta
            address = Address.objects.filter(user=request.user, address_type=address_type).first()
            if address:
                address.street = request.POST.get('street', address.street)
                address.neighborhood = request.POST.get('neighborhood', address.neighborhood)
                address.city = request.POST.get('city', address.city)
                address.state = request.POST.get('state', address.state)
                address.zip_code = request.POST.get('zip_code', address.zip_code)
                address.save()

            defaults = address_fields

            Address.objects.update_or_create(
                user=request.user,
                address_type=address_type,
                defaults=defaults
            )
            messages.success(request, 'Dirección creada exitosamente.')
            return redirect('courses:course_list')  # Redirect to course list after successful creation
    else:
        form = AddressForm()
    context = {
        'form': form,
        'address_type': address_type,
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

class DirectivesUpdateView(UpdateView):
    model = Directives
    form_class = DirectivesForm
    template_name = 'dashboard.html'

class DirectivesDeleteView(DeleteView):
    model = Directives
    template_name = 'dashboard.html'
    success_url = reverse_lazy('directives-list')  # Replace 'directives-list' with the name of your list view URL

