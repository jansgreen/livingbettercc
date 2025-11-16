from django.shortcuts import render
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import FormDefinition, FormField, CompletedForm
from .forms import FormDefinitionForm, FormFieldForm
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
# formbuilder/views.py
from django.shortcuts import render, redirect
from .utils import generate_dynamic_form
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User


def facilitador_list_view(request):
    facilitadores = User.objects.filter(groups__name='facilitador')
    context = {
        'facilitadores': facilitadores
    }
    return render(request, 'formbuilder/facilitador_list.html', context)

# FormDefinition CRUD - function-based views
def form_list(request):
    forms = FormDefinition.objects.all()
    return render(request, 'formbuilder/form_list.html', {'forms': forms})

def form_detail(request, pk):
    form_obj = get_object_or_404(FormDefinition, pk=pk)
    return render(request, 'formbuilder/form_detail.html', {'form': form_obj})

@require_http_methods(["GET", "POST"])
def form_create(request):
    if request.method == 'POST':
        form = FormDefinitionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('formbuilder:form_list'))
    else:
        form = FormDefinitionForm()
    return render(request, 'formbuilder/form_form.html', {'form': form})

@require_http_methods(["GET", "POST"])
def form_update(request, pk):
    instance = get_object_or_404(FormDefinition, pk=pk)
    if request.method == 'POST':
        form = FormDefinitionForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(reverse('formbuilder:form_list'))
    else:
        form = FormDefinitionForm(instance=instance)
    return render(request, 'formbuilder/form_form.html', {'form': form})

@require_http_methods(["GET", "POST"])
def form_delete(request, pk):
    instance = get_object_or_404(FormDefinition, pk=pk)
    if request.method == 'POST':
        instance.delete()
        return redirect(reverse('formbuilder:form_list'))
    return render(request, 'formbuilder/form_confirm_delete.html', {'object': instance})

# FormField CRUD - function-based views
@require_http_methods(["GET", "POST"])
def field_create(request, form_pk):
    parent_form = get_object_or_404(FormDefinition, pk=form_pk)
    if request.method == 'POST':
        form = FormFieldForm(request.POST)
        if form.is_valid():
            field = form.save(commit=False)
            field.form = parent_form
            field.save()
            return redirect(reverse('formbuilder:form_detail', args=[parent_form.pk]))
    else:
        form = FormFieldForm(initial={'form': form_pk})
    return render(request, 'formbuilder/field_form.html', {'form': form})

@require_http_methods(["GET", "POST"])
def field_update(request, pk):
    instance = get_object_or_404(FormField, pk=pk)
    if request.method == 'POST':
        form = FormFieldForm(request.POST, instance=instance)
        if form.is_valid():
            field = form.save()
            return redirect(reverse('formbuilder:form_detail', args=[field.form.pk]))
    else:
        form = FormFieldForm(instance=instance)
    return render(request, 'formbuilder/field_form.html', {'form': form})

@require_http_methods(["GET", "POST"])
def field_delete(request, pk):
    instance = get_object_or_404(FormField, pk=pk)
    parent_pk = instance.form.pk
    if request.method == 'POST':
        instance.delete()
        return redirect(reverse('formbuilder:form_detail', args=[parent_pk]))
    return render(request, 'formbuilder/field_confirm_delete.html', {'object': instance})

def render_form(request, form_name):
    form_obj = get_object_or_404(FormDefinition, name=form_name)
    DynamicForm = generate_dynamic_form(form_name)
    if not DynamicForm:
        return render(request, 'formbuilder/not_found.html', {'form_name': form_name})
    if not request.user.is_authenticated:
        if request.GET.get('facilitador'):
            request.session['assign_facilitador'] = True
        next_url = request.get_full_path()
        register_url = reverse('facilitador_register')
        return redirect(f"{register_url}?next={next_url}")

    if request.method == 'POST':
        form = DynamicForm(request.POST)
        if form.is_valid():
            # Aqui tengo que guardar los datos del form y en un nuevo model CRUD, para los formularios ya completados.
            completed_form = CompletedForm.objects.create(
                user=request.user,
                form_name=form_name,
                titulo=form.cleaned_data.get('titulo', ''),
                descripcion=form.cleaned_data.get('descripcion', ''),
                form_data=form.cleaned_data
            )
            completed_form.save()
            messages.success(request, f'Formulario guardado con éxito.')
            return render(request, 'formbuilder/success.html')
    else:
        form = DynamicForm()
    context={
        'form_obj': form_obj,
        'form': form, 
        'form_name': form_name

    }

    return render(request, 'formbuilder/render_form.html', context)

# Completed Forms Views
def completed_forms_list(request):
    # Require the user to be a tecnico (or staff) to view this listing.
    # If the user is not authenticated or not a tecnico, redirect them to the
    # tecnico registration page and include `next` so they return here after
    # registering.
    is_tecnico = request.user.groups.filter(name='tecnico').exists() if request.user.is_authenticated else False
    if not request.user.is_authenticated or (not is_tecnico and not request.user.is_staff):
        next_url = request.get_full_path()
        register_url = reverse('tecnico_register')
        return redirect(f"{register_url}?next={next_url}")

    completed_forms = CompletedForm.objects.all()
    if not completed_forms:
        messages.info(request, 'No hay formularios completados.')
    context = {
        'completed_forms': completed_forms
    }
    return render(request, 'formbuilder/completed/completed_forms.html', context)

def completed_forms_detail(request, pk):
    # Allow the owner or staff users to view the completed form.
    # Previous implementation filtered by `user=request.user` which causes a 404
    # when an admin or another user tries to view someone else's completed form
    # (e.g. from the facilitador list). We'll fetch by pk and then enforce
    # permission: owner or staff can view, others get a 404.
    completed_form = get_object_or_404(CompletedForm, pk=pk)
    # Allow owner, staff, or users in group 'tecnico' to view the completed form
    is_tecnico = request.user.groups.filter(name='tecnico').exists() if request.user.is_authenticated else False
    if completed_form.user != request.user and not request.user.is_staff and not is_tecnico:
        # Keep previous behavior (404) for non-authorized users.
        raise Http404("No encontrado")
    return render(request, 'formbuilder/completed/completed_form_detail.html', {'completed_form': completed_form})

def completed_forms_edit(request, pk):
    completed_form = get_object_or_404(CompletedForm, pk=pk, user=request.user)
    DynamicForm = generate_dynamic_form(completed_form.form_name)
    if not DynamicForm:
        return render(request, 'formbuilder/not_found.html', {'form_name': completed_form.form_name})

    if request.method == 'POST':
        form = DynamicForm(request.POST)
        if form.is_valid():
            completed_form.form_data = form.cleaned_data
            completed_form.save()
            messages.success(request, f'Formulario actualizado con éxito.')
            return redirect('formbuilder:completed_forms_detail', pk=completed_form.pk)
    else:
        form = DynamicForm(initial=completed_form.form_data)

    context = {
        'form': form,
        'completed_form': completed_form,
    }
    return render(request, 'formbuilder/completed/edit_completed_form.html', context)

def facilitadores_por_formulario(request):
    completed_forms = CompletedForm.objects.exclude(distrito__isnull=True).exclude(distrito__exact='')
    context = {
        'completed_forms': completed_forms
    }
    return render(request, 'formbuilder/completed_facilitadores_por_formulario.html', context)


@require_http_methods(["POST"])
def share_with_facilitadores(request, pk):
    """Handle 'share with facilitadores' action for a CompletedForm.
    For now this is a placeholder action: it validates that the requester
    is allowed to share (owner, staff or tecnico) and sets a success message
    before redirecting to the completed form detail. Later we can extend
    this to send emails or toggles on the model.
    """
    completed_form = get_object_or_404(CompletedForm, pk=pk)
    is_tecnico = request.user.groups.filter(name='tecnico').exists() if request.user.is_authenticated else False
    if completed_form.user != request.user and not request.user.is_staff and not is_tecnico:
        raise Http404("No encontrado")

    # Build a short, shareable URL that redirects to the completed form detail.
    share_path = reverse('formbuilder:shared_completed_form', args=[completed_form.pk])
    share_url = request.build_absolute_uri(share_path)

    # Render a small page that shows the shareable link and a copy-to-clipboard button.
    context = {
        'share_url': share_url,
        'completed_form': completed_form,
    }
    return render(request, 'formbuilder/shared/shared_link.html', context)


def shared_completed_form(request, pk):
    """Public short link. If the visitor is authenticated and allowed, redirect
    to the completed form detail. If not authenticated, redirect to the
    tecnico registration page and set `next` so they return to the detail after
    registering.
    """
    completed_form = get_object_or_404(CompletedForm, pk=pk)
    detail_path = reverse('formbuilder:completed_forms_detail', args=[completed_form.pk])

    # If user is authenticated and authorized, redirect to detail
    if request.user.is_authenticated:
        is_tecnico = request.user.groups.filter(name='tecnico').exists()
        if completed_form.user == request.user or request.user.is_staff or is_tecnico:
            return redirect(detail_path)
        # Authenticated but not authorized -> 404
        raise Http404("No encontrado")

    # Not authenticated: redirect to tecnico registration with next=detail_path
    register_url = reverse('tecnico_register')
    return redirect(f"{register_url}?next={detail_path}")

def my_user_complete_forms(request):
    completed_forms = CompletedForm.objects.filter(user=request.user)
    context = {
        'completed_forms': completed_forms
    }
    return render(request, 'formbuilder/completed/my_user_completed_forms.html', context)