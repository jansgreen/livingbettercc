from django.shortcuts import render
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import FormDefinition, FormField, CompletedForm
from .forms import FormDefinitionForm, FormFieldForm, FacilitadorRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
# formbuilder/views.py
from django.shortcuts import render, redirect
from .utils import generate_dynamic_form, build_ordered_responses
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.files.storage import default_storage
from django.contrib.auth import login, get_backends
from django.utils.text import slugify
import os
from .models import FormDefinition, FormShareLink

def pending_forms(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Aquí puedes implementar la lógica para obtener los formularios pendientes
    # Por simplicidad, asumiremos que todos los formularios están pendientes
    pending_forms = FormDefinition.objects.all()
    # Adjuntar el pk del último formulario completado por el usuario para cada definición,
    # de modo que el botón "Editar" pueda apuntar al recurso correcto.
    for f in pending_forms:
        f.user_completed_pk = (
            CompletedForm.objects
            .filter(user=request.user, form_name=f.name)
            .order_by('-submitted_at')
            .values_list('pk', flat=True)
            .first()
        )
    
    context = {
        'pending_forms': pending_forms
    }
    return render(request, 'formbuilder/pending_forms.html', context)

def edit_forms(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Aquí puedes implementar la lógica para obtener los formularios que el usuario puede editar
    # Por simplicidad, asumiremos que todos los formularios pueden ser editados
    editable_forms = FormDefinition.objects.all()
    
    context = {
        'editable_forms': editable_forms
    }
    return render(request, 'formbuilder/edit_forms.html', context)

@require_http_methods(["GET", "POST"])
def enroll_facilitador(request):
    form = FacilitadorRegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            # FIX: handle both return types (User or tuple)
            result = form.save()
            user = None
            distrito = ''
            address = None
            if isinstance(result, tuple):
                # Expected: (user, distrito, address) or shorter
                user = result[0] if len(result) > 0 else None
                distrito = result[1] if len(result) > 1 else ''
                address = result[2] if len(result) > 2 else None
            elif isinstance(result, User):
                user = result
            else:
                # Fallback for custom object with attributes
                user = getattr(result, 'user', None)
                distrito = getattr(result, 'distrito', '')
                address = getattr(result, 'address', None)

            if not isinstance(user, User) or user is None:
                messages.error(request, 'No se pudo crear el usuario del facilitador.')
                return render(request, 'formbuilder/facilitador/enroll_facilitador.html', {'form': form})

            # Asignar grupo facilitador
            group, _ = Group.objects.get_or_create(name='facilitador')
            user.groups.add(group)

            # Log in so address_create can bind address.user = request.user
            backend = get_backends()[0]
            user.backend = f"{backend.__module__}.{backend.__class__.__name__}"
            login(request, user)

            messages.success(request, 'Facilitador registrado exitosamente.')

            # Redirigir a address_create con kwargs correctos (address_type y pk)
            next_url = reverse('authentication:address_create', kwargs={
                'address_type': 'residencial',
                'pk': user.id,
            })
            return redirect(next_url)
        else:
            messages.error(request, f'{form.errors} Por favor corrige los errores en el formulario.')
    context = {'form': form}
    return render(request, 'formbuilder/facilitador/enroll_facilitador.html', context)

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
        form = FormDefinitionForm(request.POST, request.FILES)
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
        form = FormDefinitionForm(request.POST, request.FILES, instance=instance)
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

    subtitle = (form_obj.description or '').strip()

    file_field_names = set(
        form_obj.fields.filter(field_type='files').values_list('name', flat=True)
    )

    def _save_uploaded_files(uploaded_files, *, user_id: int, form_name: str, field_name: str) -> list[str]:
        saved_urls: list[str] = []
        if not uploaded_files:
            return saved_urls

        safe_form = slugify(form_name)[:60] or 'form'
        safe_field = slugify(field_name)[:60] or 'files'
        base_dir = os.path.join('form_uploads', safe_form, str(user_id), safe_field)

        for f in uploaded_files:
            filename = f.name
            path = default_storage.save(os.path.join(base_dir, filename), f)
            saved_urls.append(default_storage.url(path))
        return saved_urls

    if request.method == 'POST':
        post_data = request.POST

        # If the form includes the 'objetivo_razon_motivo' field, we use the
        # FormDefinition.description as its fixed value (subtitle).
        if subtitle and hasattr(DynamicForm, 'base_fields') and 'objetivo_razon_motivo' in DynamicForm.base_fields:
            if 'objetivo_razon_motivo' not in post_data:
                post_data = post_data.copy()
                post_data['objetivo_razon_motivo'] = subtitle

        form = DynamicForm(post_data, request.FILES)
        if form.is_valid():
            json_safe_data = dict(form.cleaned_data)

            # Persist uploaded files and store URLs (JSON-safe) instead of UploadedFile objects.
            for field_name in file_field_names:
                uploaded_list = form.cleaned_data.get(field_name) or []
                if uploaded_list and not isinstance(uploaded_list, (list, tuple)):
                    uploaded_list = [uploaded_list]
                json_safe_data[field_name] = _save_uploaded_files(
                    uploaded_list,
                    user_id=request.user.id,
                    form_name=form_name,
                    field_name=field_name,
                )

            # Aqui tengo que guardar los datos del form y en un nuevo model CRUD, para los formularios ya completados.
            completed_form = CompletedForm.objects.create(
                user=request.user,
                form_name=form_name,
                titulo=form.cleaned_data.get('titulo', ''),
                descripcion=subtitle or form.cleaned_data.get('descripcion', ''),
                form_data=json_safe_data
            )
            completed_form.save()
            messages.success(request, f'Formulario guardado con éxito.')
            return render(request, 'formbuilder/success.html')
    else:
        initial = {}
        if subtitle and hasattr(DynamicForm, 'base_fields') and 'objetivo_razon_motivo' in DynamicForm.base_fields:
            initial['objetivo_razon_motivo'] = subtitle
        form = DynamicForm(initial=initial)
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
    form_obj = FormDefinition.objects.filter(name=completed_form.form_name).first()
    responses = build_ordered_responses(completed_form.form_name, completed_form.form_data)
    return render(
        request,
        'formbuilder/completed/completed_form_detail.html',
        {
            'completed_form': completed_form,
            'form_obj': form_obj,
            'responses': responses,
        },
    )

def completed_forms_edit(request, pk):
    completed_form = get_object_or_404(CompletedForm, pk=pk, user=request.user)
    DynamicForm = generate_dynamic_form(completed_form.form_name)
    if not DynamicForm:
        return render(request, 'formbuilder/not_found.html', {'form_name': completed_form.form_name})

    form_obj = FormDefinition.objects.filter(name=completed_form.form_name).first()
    file_field_names = set()
    if form_obj:
        file_field_names = set(
            form_obj.fields.filter(field_type='files').values_list('name', flat=True)
        )

    subtitle = (completed_form.descripcion or (form_obj.description if form_obj else '') or '').strip()

    if request.method == 'POST':
        post_data = request.POST
        if subtitle and hasattr(DynamicForm, 'base_fields') and 'objetivo_razon_motivo' in DynamicForm.base_fields:
            if 'objetivo_razon_motivo' not in post_data:
                post_data = post_data.copy()
                post_data['objetivo_razon_motivo'] = subtitle

        form = DynamicForm(post_data, request.FILES)
        if form.is_valid():
            json_safe_data = dict(form.cleaned_data)
            existing_data = completed_form.form_data or {}

            # Replace attachments only when new files are uploaded; otherwise keep existing URLs.
            for field_name in file_field_names:
                uploaded_list = form.cleaned_data.get(field_name) or []
                if uploaded_list and not isinstance(uploaded_list, (list, tuple)):
                    uploaded_list = [uploaded_list]

                if uploaded_list:
                    safe_form = slugify(completed_form.form_name)[:60] or 'form'
                    safe_field = slugify(field_name)[:60] or 'files'
                    base_dir = os.path.join('form_uploads', safe_form, str(request.user.id), safe_field)
                    saved_urls: list[str] = []
                    for f in uploaded_list:
                        path = default_storage.save(os.path.join(base_dir, f.name), f)
                        saved_urls.append(default_storage.url(path))
                    json_safe_data[field_name] = saved_urls
                else:
                    json_safe_data[field_name] = existing_data.get(field_name, [])

            completed_form.form_data = json_safe_data
            if subtitle:
                completed_form.descripcion = subtitle
            completed_form.save()
            messages.success(request, f'Formulario actualizado con éxito.')
            return redirect('formbuilder:completed_forms_detail', pk=completed_form.pk)
    else:
        initial = dict(completed_form.form_data or {})
        if subtitle and hasattr(DynamicForm, 'base_fields') and 'objetivo_razon_motivo' in DynamicForm.base_fields:
            initial.setdefault('objetivo_razon_motivo', subtitle)
        form = DynamicForm(initial=initial)

    context = {
        'form': form,
        'form_obj': form_obj,
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

# shared form definition view UUID

def share_form_definition(request, pk):
    """
    Genera un link compartible para un FormDefinition (plantilla).
    Recomendado: solo permitir a staff / tecnico / owner (según tu lógica).
    """
    if not request.user.is_authenticated:
        next_url = request.get_full_path()
        return redirect(f"{reverse('authentication:login')}?next={next_url}")

    form_obj = get_object_or_404(FormDefinition, pk=pk)

    # TODO: aquí validas permisos reales (staff/tecnico/etc)
    # Ejemplo mínimo:
    # if not request.user.is_staff and not request.user.groups.filter(name="tecnico").exists():
    #     raise Http404("No encontrado")

    link = FormShareLink.objects.create(form=form_obj, created_by=request.user)

    share_url = request.build_absolute_uri(
        reverse("formbuilder:shared_form_definition", kwargs={"token": link.token})
    )

    return render(request, "formbuilder/shared/shared_link.html", {
        "share_url": share_url,
        "form_obj": form_obj,
    })

def shared_form_definition(request, token):
    """
    Link público (token). Si no está autenticado → login/registro con next a este mismo link.
    Si está autenticado → redirige a render_form del form.
    """
    link = get_object_or_404(FormShareLink, token=token, is_active=True)
    form_obj = link.form

    # Si NO está autenticado, mandarlo a login o register con next=este mismo link
    if not request.user.is_authenticated:
        next_url = request.get_full_path()
        # usa login o register, según tu flujo
        return redirect(f"{reverse('authentication:login')}?next={next_url}")

    # Si necesitas forzar grupo "facilitador", aquí es donde lo manejas:
    # if not request.user.groups.filter(name="facilitador").exists() and not request.user.is_staff:
    #     messages.info(request, "Necesitas cuenta de facilitador para completar este formulario.")
    #     next_url = request.get_full_path()
    #     return redirect(f"{reverse('authentication:register')}?next={next_url}")

    # Ya autenticado y autorizado → render_form normal
    return redirect(reverse("formbuilder:render_form", kwargs={"form_name": form_obj.name}))

def my_user_complete_forms(request):
    completed_forms = CompletedForm.objects.filter(user=request.user)
    context = {
        'completed_forms': completed_forms
    }
    return render(request, 'formbuilder/completed/my_user_completed_forms.html', context)