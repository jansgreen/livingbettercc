from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from .models import FormDefinition, FormField, CompletedForm
from .forms import FormDefinitionForm, FormFieldForm, FacilitadorRegistrationForm, TrimestralReportForm
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
# formbuilder/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .utils import generate_dynamic_form, build_ordered_responses
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.core.files.storage import default_storage
from django.contrib.auth import login, get_backends
from django.utils.text import slugify
import os
from .models import FormDefinition, FormShareLink
from authentication.models.profiles import Profiles
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import EmailMessage
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from urllib.parse import urlencode
from collections import defaultdict
from core.group_utils import has_group, group_q, ensure_group



def _is_facilitador(user) -> bool:
    return has_group(user, "facilitadores")

def _is_tecnico(user) -> bool:
    return has_group(user, "tecnicos")

def _is_staff(user) -> bool:
    return bool(user and user.is_authenticated and user.is_staff)

def _require_facilitador_or_staff(request):
    if False:
        next_url = request.get_full_path()
        register_url = reverse('authentication:facilitador_register')
        return redirect(f"{register_url}?next={next_url}")
    if not (_is_facilitador(request.user) or _is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
    return None

def pending_forms(request):
    guard = _require_facilitador_or_staff(request)
    if guard:
        return guard
    # Aquí puedes implementar la lógica para obtener los formularios pendientes
    # Por simplicidad, asumiremos que todos los formularios están pendientes
    pending_forms = FormDefinition.objects.all()
    # Adjuntar el pk del último formulario completado por el usuario para cada definición,
    # de modo que el botón "Editar" pueda apuntar al recurso correcto.
    for f in pending_forms:
        f.user_completed_pk = (
            CompletedForm.objects
            .filter(user=request.user)
            .filter(Q(form=f) | Q(form_name=f.name))
            .order_by('-submitted_at')
            .values_list('pk', flat=True)
            .first()
        )
    
    context = {
        'pending_forms': pending_forms
    }
    return render(request, 'formbuilder/pending_forms.html', context)

def edit_forms(request):
    guard = _require_facilitador_or_staff(request)
    if guard:
        return guard
    
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
            group = ensure_group('Facilitadores')
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
    if not (_is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
    facilitadores = User.objects.filter(group_q('facilitadores')).distinct()
    context = {
        'facilitadores': facilitadores
    }
    return render(request, 'formbuilder/facilitador_list.html', context)

# FormDefinition CRUD - function-based views
def form_list(request):
    if not _is_staff(request.user):
        raise Http404("No encontrado")
    forms = FormDefinition.objects.all()
    return render(request, 'formbuilder/form_list.html', {'forms': forms})

def form_detail(request, pk):
    if not _is_staff(request.user):
        raise Http404("No encontrado")
    form_obj = get_object_or_404(FormDefinition, pk=pk)
    return render(request, 'formbuilder/form_detail.html', {'form': form_obj})

@require_http_methods(["GET", "POST"])
def form_create(request):
    if not _is_staff(request.user):
        raise Http404("No encontrado")
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
    if not _is_staff(request.user):
        raise Http404("No encontrado")
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
    if not _is_staff(request.user):
        raise Http404("No encontrado")
    instance = get_object_or_404(FormDefinition, pk=pk)
    if request.method == 'POST':
        instance.delete()
        return redirect(reverse('formbuilder:form_list'))
    return render(request, 'formbuilder/form_confirm_delete.html', {'object': instance})

# FormField CRUD - function-based views
@require_http_methods(["GET", "POST"])
def field_create(request, form_pk):
    if not _is_staff(request.user):
        raise Http404("No encontrado")
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
    if not _is_staff(request.user):
        raise Http404("No encontrado")
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
    if not _is_staff(request.user):
        raise Http404("No encontrado")
    instance = get_object_or_404(FormField, pk=pk)
    parent_pk = instance.form.pk
    if request.method == 'POST':
        instance.delete()
        return redirect(reverse('formbuilder:form_detail', args=[parent_pk]))
    return render(request, 'formbuilder/field_confirm_delete.html', {'object': instance})

def render_form(request, form_name):
    """
    Renderiza y procesa un FormDefinition dinámico.
    - Si el usuario no está autenticado: redirige a registro/login preservando `next`.
    - Evita loops de `next` apuntando al login.
    - En POST: guarda CompletedForm con data JSON-safe (incluye URLs de archivos subidos).
    """

    form_obj = get_object_or_404(FormDefinition, name=form_name)

    DynamicForm = generate_dynamic_form(form_obj)
    if not DynamicForm:
        return render(request, "formbuilder/not_found.html", {"form_name": form_name})

    guard = _require_facilitador_or_staff(request)
    if guard:
        return guard

    # ---------------------------------------------------------------------
    # Auth gate (aplica tanto GET como POST)
    # ---------------------------------------------------------------------
    if not request.user.is_authenticated:
        # Si viene marcado como facilitador, guarda flag en sesión
        if request.GET.get("facilitador"):
            request.session["assign_facilitador"] = True

        next_url = request.get_full_path()

        # Previene next inseguro / externo
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"

        # Previene loop: si el next ya es el login/register, lo mandamos a home
        login_url = settings.LOGIN_URL or "/accounts/login/"
        register_url = reverse("facilitador_register")

        if next_url.startswith(login_url) or next_url.startswith(register_url):
            next_url = "/"

        # Redirige a registro (o cambia a tu login si prefieres)
        qs = urlencode({"next": next_url})
        return redirect(f"{register_url}?{qs}")

    # ---------------------------------------------------------------------
    # Datos del formulario / campos especiales
    # ---------------------------------------------------------------------
    subtitle = (form_obj.description or "").strip()

    file_field_names = set(
        form_obj.fields.filter(field_type="files").values_list("name", flat=True)
    )

    def _save_uploaded_files(
        uploaded_files, *, user_id: int, form_name: str, field_name: str
    ) -> list[str]:
        saved_urls: list[str] = []
        if not uploaded_files:
            return saved_urls

        safe_form = slugify(form_name)[:60] or "form"
        safe_field = slugify(field_name)[:60] or "files"
        base_dir = os.path.join("form_uploads", safe_form, str(user_id), safe_field)

        for f in uploaded_files:
            filename = f.name
            path = default_storage.save(os.path.join(base_dir, filename), f)
            saved_urls.append(default_storage.url(path))
        return saved_urls

    # ---------------------------------------------------------------------
    # POST (guardar)
    # ---------------------------------------------------------------------
    if request.method == "POST":
        post_data = request.POST

        # Si existe el campo objetivo_razon_motivo, fija el valor con description
        if (
            subtitle
            and hasattr(DynamicForm, "base_fields")
            and "objetivo_razon_motivo" in DynamicForm.base_fields
        ):
            if "objetivo_razon_motivo" not in post_data:
                post_data = post_data.copy()
                post_data["objetivo_razon_motivo"] = subtitle

        form = DynamicForm(post_data, request.FILES)

        if form.is_valid():
            json_safe_data = dict(form.cleaned_data)

            # Guardar archivos subidos como URLs (JSON-safe)
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

            CompletedForm.objects.create(
                user=request.user,
                form=form_obj,
                form_name=form_name,
                titulo=form.cleaned_data.get("titulo", ""),
                descripcion=subtitle or form.cleaned_data.get("descripcion", ""),
                form_data=json_safe_data,
            )

            messages.success(request, "Formulario guardado con éxito.")
            return render(request, "formbuilder/success.html", {"form_obj": form_obj})

        # Si no es válido, cae al render final con errores

    # ---------------------------------------------------------------------
    # GET (inicial)
    # ---------------------------------------------------------------------
    else:
        initial = {}
        if (
            subtitle
            and hasattr(DynamicForm, "base_fields")
            and "objetivo_razon_motivo" in DynamicForm.base_fields
        ):
            initial["objetivo_razon_motivo"] = subtitle
        form = DynamicForm(initial=initial)

    context = {
        "form_obj": form_obj,
        "form": form,
        "form_name": form_name,
    }
    return render(request, "formbuilder/render_form.html", context)


def render_form_by_id(request, form_id):
    form_obj = get_object_or_404(FormDefinition, pk=form_id)
    return render_form(request, form_obj.name)

# Completed Forms Views
def completed_forms_list(request):
    if not request.user.is_authenticated:
        next_url = request.get_full_path()
        register_url = reverse('authentication:tecnico_register')
        return redirect(f"{register_url}?next={next_url}")

    if _is_staff(request.user):
        completed_forms = CompletedForm.objects.all()
    elif _is_tecnico(request.user):
        completed_forms = CompletedForm.objects.filter(user__in=User.objects.filter(group_q('facilitadores'))).distinct()
    else:
        raise Http404("No encontrado")
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
    if completed_form.user != request.user and not _is_staff(request.user) and not _is_tecnico(request.user):
        # Keep previous behavior (404) for non-authorized users.
        raise Http404("No encontrado")
    form_obj = completed_form.form or FormDefinition.objects.filter(name=completed_form.form_name).first()
    responses = build_ordered_responses(completed_form.form_name, completed_form.form_data)
    responses_by_name = {r.get('name'): r for r in responses}
    handled_names = {
        'centro_educativo',
        'responsables',
        'fechas',
        'temas_impartidos',
        'objetivo_razon_motivo',
        'impacto_antes_decepcion_escolar',
        'impacto_antes_conflicto_familiar',
        'impacto_antes_hogares_disfuncionales',
        'impacto_antes_problemas_salud',
        'impacto_antes_problemas_mentales',
        'impacto_positivo_nivel_escolar',
        'impacto_positivo_nivel_familiar',
        'impacto_positivo_social',
        'mejora_decepcion_escolar',
        'anexos',
    }
    remaining_responses = [r for r in responses if r.get('name') not in handled_names]
    tecnico_summary = None
    if _is_tecnico(request.user) or _is_staff(request.user):
        all_forms = CompletedForm.objects.filter(user__in=User.objects.filter(group_q('facilitadores'))).distinct()
        tecnico_summary = _aggregate_completed_forms(all_forms)

    return render(
        request,
        'formbuilder/completed/completed_form_detail.html',
        {
            'completed_form': completed_form,
            'form_obj': form_obj,
            'responses': responses,
            'responses_by_name': responses_by_name,
            'remaining_responses': remaining_responses,
            'tecnico_summary': tecnico_summary,
        },
    )

def _extract_numeric(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return value
    try:
        s = str(value).strip()
        if not s:
            return 0
        s = s.replace(",", ".")
        return float(s)
    except Exception:
        return 0

def _format_distrito(value):
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if s.isdigit():
        return s.zfill(2)
    return s

def _aggregate_completed_forms(completed_forms):
    totals = defaultdict(float)
    centers = []
    center_index = set()
    districts = []
    temas = ""
    objetivo = ""

    for cf in completed_forms:
        data = cf.form_data or {}
        center = data.get("centro_educativo")
        if center and center not in center_index:
            centers.append({"name": center, "pk": cf.pk})
            center_index.add(center)
        district = _format_distrito(cf.distrito)
        if district and district not in districts:
            districts.append(district)

        if not temas:
            temas = data.get("temas_impartidos") or ""
        if not objetivo:
            objetivo = data.get("objetivo_razon_motivo") or ""

        for key, val in data.items():
            num = _extract_numeric(val)
            if num != 0:
                totals[key] += num

    return {
        "totals": dict(totals),
        "centers": centers,
        "districts": districts,
        "temas": temas,
        "objetivo": objetivo,
    }

def panel_tecnico(request):
    if not (_is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
    forms = FormDefinition.objects.all()
    completed_forms = (
        CompletedForm.objects
        .filter(user__in=User.objects.filter(group_q('facilitadores')))
        .select_related('user')
        .order_by('-submitted_at')
    )
    paginator = Paginator(completed_forms, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'forms': forms,
        'completed_forms': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'trimestral/panel_tecnico.html', context)

def panel_tecnico_user(request, user_id):
    if not (_is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
    user = get_object_or_404(User, pk=user_id)
    profile = Profiles.objects.filter(user=user).first()
    completed_forms = (
        CompletedForm.objects
        .filter(user=user)
        .order_by('-submitted_at')
    )
    context = {
        'profile': profile,
        'target_user': user,
        'completed_forms': completed_forms,
    }
    return render(request, 'trimestral/panel_tecnico_user.html', context)

def tecnico_report_general(request):
    if not (_is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
    completed_forms = CompletedForm.objects.filter(user__in=User.objects.filter(group_q('facilitadores'))).distinct()
    summary = _aggregate_completed_forms(completed_forms)
    form_obj = FormDefinition.objects.first()
    return render(request, "trimestral/tecnico_general.html", {
        "form_obj": form_obj,
        "summary": summary,
        "completed_forms": completed_forms,
    })

def tecnico_report_detail(request, pk):
    if not (_is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
    anchor = get_object_or_404(CompletedForm, pk=pk)
    center = (anchor.form_data or {}).get("centro_educativo")
    if not center:
        raise Http404("No encontrado")
    all_forms = CompletedForm.objects.filter(user__in=User.objects.filter(group_q('facilitadores'))).distinct()
    center_forms = [cf for cf in all_forms if (cf.form_data or {}).get("centro_educativo") == center]
    summary = _aggregate_completed_forms(center_forms)
    form_obj = anchor.form or FormDefinition.objects.filter(name=anchor.form_name).first()
    return render(request, "trimestral/tecnico_detail.html", {
        "form_obj": form_obj,
        "summary": summary,
        "center": center,
        "completed_forms": center_forms,
        "anchor": anchor,
    })

def completed_forms_edit(request, pk):
    completed_form = get_object_or_404(CompletedForm, pk=pk)
    if completed_form.user != request.user and not _is_staff(request.user):
        raise Http404("No encontrado")
    DynamicForm = generate_dynamic_form(completed_form.form or completed_form.form_name)
    if not DynamicForm:
        return render(request, 'formbuilder/not_found.html', {'form_name': completed_form.form_name})

    form_obj = completed_form.form or FormDefinition.objects.filter(name=completed_form.form_name).first()
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
    if not (_is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")
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
    if completed_form.user != request.user and not _is_staff(request.user) and not _is_tecnico(request.user):
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
        if completed_form.user == request.user or _is_staff(request.user) or _is_tecnico(request.user):
            return redirect(detail_path)
        # Authenticated but not authorized -> 404
        raise Http404("No encontrado")

    # Not authenticated: redirect to tecnico registration with next=detail_path
    register_url = reverse('authentication:tecnico_register')
    return redirect(f"{register_url}?next={detail_path}")

# shared form definition view UUID

def share_form_definition(request, pk):
    """
    Genera un link compartible para un FormDefinition (plantilla).
    Recomendado: solo permitir a staff / tecnico / owner (según tu lógica).
    """
    if not (_is_staff(request.user) or _is_tecnico(request.user)):
        raise Http404("No encontrado")

    form_obj = get_object_or_404(FormDefinition, pk=pk)

    link = FormShareLink.objects.create(form=form_obj, created_by=request.user)

    share_url = request.build_absolute_uri(
        reverse("formbuilder:shared_form_definition", kwargs={"token": link.token})
    )

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip()
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Ingresa un email válido.")
        else:
            subject = "Formulario para completar - LivingBetterCC"
            message_text = (
                "Hola,\n\n"
                "Te compartimos el enlace para completar el formulario:\n\n"
                f"{share_url}\n\n"
                "Si no solicitaste esto, puedes ignorar este correo."
            )
            EmailMessage(
                subject=subject,
                body=message_text,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
                to=[email],
            ).send(fail_silently=False)
            messages.success(request, "Enlace enviado correctamente.")

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
        return redirect(f"{reverse('authentication:facilitador_register')}?next={next_url}")

    # Si necesitas forzar grupo "facilitador", aquí es donde lo manejas:
    # if not request.user.groups.filter(name="facilitador").exists() and not request.user.is_staff:
    #     messages.info(request, "Necesitas cuenta de facilitador para completar este formulario.")
    #     next_url = request.get_full_path()
    #     return redirect(f"{reverse('authentication:register')}?next={next_url}")

    if not (_is_facilitador(request.user) or _is_tecnico(request.user) or _is_staff(request.user)):
        raise Http404("No encontrado")

    # Ya autenticado y autorizado → render_form normal
    return redirect(reverse("formbuilder:render_form_by_id", kwargs={"form_id": form_obj.id}))

def shared_form_entry(request, token):
    link = get_object_or_404(FormShareLink, token=token, is_active=True)

    if not link.is_valid():
        # puedes renderizar template "link expirado"
        return redirect("home")  # o 404

    # Si NO está autenticado => enviar a login/registro con next seguro
    if not request.user.is_authenticated:
        next_url = request.get_full_path()

        # Valida que next sea seguro
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            next_url = reverse("home")

        return redirect(f"{reverse('authentication:facilitador_register')}?next={next_url}")

    # Ya autenticado: aquí validas rol/grupo (facilitador)
    if not _is_facilitador(request.user) and not _is_staff(request.user):
        return redirect("home")  # o 403

    # Redirige al form real (sin exponer ID público si no quieres)
    return redirect("formbuilder:render_form_by_id", form_id=link.form.id)

@login_required
def my_user_complete_forms(request):
    completed_forms = CompletedForm.objects.filter(user=request.user)
    context = {
        'completed_forms': completed_forms
    }
    return render(request, 'formbuilder/completed/my_user_completed_forms.html', context)


@login_required
def tabla_trimestral(request):
    form = TrimestralReportForm()
    if request.method == 'POST':
        form = TrimestralReportForm(request.POST, isinstance=request.user,)
        if form.is_valid():
            form.save()
            return redirect('formbuilder:tabla_trimestral')
    else:
        form = TrimestralReportForm()
    return render(request, 'formbuilder/trimestral/tabla_trimestral.html', {'form': form, 'reports': reports})
