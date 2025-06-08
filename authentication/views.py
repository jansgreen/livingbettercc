from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import ProfileForm, CustomerForm
from authentication.models.profiles import Profiles 
from authentication.models.customers import Customers

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect URL
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login after successful registration
    else:
        form = UserCreationForm()
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
    form = CustomerForm()
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.user = request.user
            customer.save()
            return redirect('checkout_complete')  # Redirect after successful submission
    context = {
        'form': form,
    }
    return render(request, 'authentication/customers.html', context)



def customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Autenticamos al usuario automáticamente
            return redirect('shop:checkout')  # O la siguiente etapa
    else:
        form = CustomerForm()
    return render(request, 'authentication/customers.html', {'form': form})
