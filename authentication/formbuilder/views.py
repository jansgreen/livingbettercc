from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import FormDefinition, FormField
from .forms import FormDefinitionForm, FormFieldForm
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
# formbuilder/views.py
from django.shortcuts import render, redirect
from .utils import generate_dynamic_form

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
    DynamicForm = generate_dynamic_form(form_name)
    if not DynamicForm:
        return render(request, 'formbuilder/not_found.html', {'form_name': form_name})

    # If user is not authenticated and the link contains a facilitator flag,
    # store a session marker and redirect to register so the user can sign up.
    # The sender can include ?facilitador=1 in the link.
    if not request.user.is_authenticated:
        # If the link contains facilitador param, set session flag so registration
        # view can assign the group after successful signup.
        if request.GET.get('facilitador'):
            request.session['assign_facilitador'] = True
        # Redirect user to register page with next pointing back to this form URL
        from django.urls import reverse
        next_url = request.get_full_path()
        register_url = reverse('register')
        return redirect(f"{register_url}?next={next_url}")

    if request.method == 'POST':
        form = DynamicForm(request.POST)
        if form.is_valid():
            # Aquí puedes guardar las respuestas si quieres
            print(form.cleaned_data)
            return render(request, 'formbuilder/success.html')
    else:
        form = DynamicForm()

    return render(request, 'formbuilder/render_form.html', {'form': form, 'form_name': form_name})
