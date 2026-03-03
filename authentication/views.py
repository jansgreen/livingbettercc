from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_backends
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from classroom.enrollments.models import Enrollment, LessonCompletion
from django.conf import settings
from .forms import BootstrapUserCreationForm, ProfileForm, CustomerForm, DirectivesForm, BootstrapAuthenticationForm
from authentication.address.forms import AddressForm
from authentication.models.profiles import Profiles 
from authentication.models.customers import Customers
from authentication.models.directives import Directives
from authentication.address.models import Address
from authentication.models.students import Students
from django.utils.http import url_has_allowed_host_and_scheme
from formbuilder.forms import FacilitadorRegistrationForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from authentication.groups.models import Invitation
from django.urls import reverse

STUDENT_GROUP_ALIASES = {"student", "students", "estudiante", "estudiantes"}
FACILITATOR_GROUP_ALIASES = {"facilitador", "facilitadores"}


def _canonical_group_name(name: str | None) -> str:
    raw = (name or "").strip()
    if not raw:
        return ""
    if raw.lower() in STUDENT_GROUP_ALIASES:
        return "estudiantes"
    if raw.lower() in FACILITATOR_GROUP_ALIASES:
        return "Facilitadores"
    return raw


def _assign_user_group(user, group_name: str | None):
    canonical = _canonical_group_name(group_name)
    if not canonical:
        return
    group, _ = Group.objects.get_or_create(name=canonical)
    user.groups.add(group)
    if canonical == "estudiantes":
        _normalize_student_groups(user)
    if canonical == "Facilitadores":
        _normalize_facilitator_groups(user)


def _resume_after_profile(request):
    """
    Reanuda la intención guardada en session luego de completar el profile.
    Prioridad:
      1) post_profile_intent (classroom)
      2) post_profile_next
      3) dashboard
    """
    intent = request.session.pop("post_profile_intent", None)
    if intent and intent.get("source") == "classroom":
        course_id = intent.get("course_id")
        if course_id:
            return redirect("courses:start_course_payment", pk=course_id)

    next_url = request.session.pop("post_profile_next", None)
    if next_url:
        return redirect(next_url)

    return redirect("dashboard")

def _safe_next_url(request, next_url: str | None, fallback_name: str = "dashboard") -> str:
    """
    Devuelve un next seguro para redirigir, evitando loops y URLs externas.
    """
    fallback = reverse(fallback_name)

    if not next_url:
        return fallback

    # Evita que te manden a login/logout (loop típico)
    blocked_prefixes = ("/auth/login", "/auth/logout", "/accounts/login", settings.LOGIN_URL.rstrip("/"))
    if any(next_url.startswith(p) for p in blocked_prefixes):
        return fallback

    # Evita open-redirect (seguridad)
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return fallback

    return next_url

def _normalize_student_groups(user):
    """Move any legacy student groups to 'estudiantes'."""
    if not user or not getattr(user, 'is_authenticated', False):
        return
    names = set(user.groups.values_list('name', flat=True))
    lowered = {name.lower() for name in names}
    if lowered.intersection(STUDENT_GROUP_ALIASES):
        group, _ = Group.objects.get_or_create(name='estudiantes')
        user.groups.add(group)
        for current_name in names:
            if current_name.lower() in STUDENT_GROUP_ALIASES and current_name != 'estudiantes':
                legacy_group = Group.objects.filter(name=current_name).first()
                if legacy_group:
                    user.groups.remove(legacy_group)


def _normalize_facilitator_groups(user):
    """Move any legacy facilitator groups to 'Facilitadores'."""
    if not user or not getattr(user, 'is_authenticated', False):
        return
    names = set(user.groups.values_list('name', flat=True))
    lowered = {name.lower() for name in names}
    if lowered.intersection(FACILITATOR_GROUP_ALIASES):
        group, _ = Group.objects.get_or_create(name='Facilitadores')
        user.groups.add(group)
        for current_name in names:
            if current_name.lower() in FACILITATOR_GROUP_ALIASES and current_name != 'Facilitadores':
                legacy_group = Group.objects.filter(name=current_name).first()
                if legacy_group:
                    user.groups.remove(legacy_group)

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
    _normalize_student_groups(user)
    _normalize_facilitator_groups(user)

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
            group, _ = Group.objects.get_or_create(name='Facilitadores')
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
    al grupo 'tecnicos'. Los técnicos pueden revisar qué formularios completaron
    los facilitadores (acceso de solo lectura).
    """
    next_url = request.GET.get('next', None)
    if request.method == 'POST':
        form = FacilitadorRegistrationForm(request.POST)
        if form.is_valid():
            user, distrito, address = form.save()
            # Asignar grupo tecnico
            from django.contrib.auth.models import Group
            group, _ = Group.objects.get_or_create(name='tecnicos')
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

# CRUD Authentication

def register_view(request):
    """
    Registro central (orquestador):
    - No ejecuta la intención (auth_intent) aquí.
    - Solo registra + login + redirige a completar Profile.
    - La intención se reanuda DESPUÉS (ej: en profile_create_view).
    """
    # Si ya está logueado, lo mandamos a un punto estable.
    # (Opcional: podrías mandarlo a profile si no existe aún)
    if request.user.is_authenticated:
        return redirect("dashboard")

    # Intención guardada (si viene de classroom/shop/invite)
    intent = request.session.get("auth_intent") or {}

    # next solo como fallback visual (por si llegas a register directo)
    query_next = request.GET.get("next")
    raw_next = intent.get("next") or query_next
    next_url = _safe_next_url(request, raw_next, fallback_name="dashboard")

    if request.method == "POST":
        post_next = request.POST.get("next")
        next_url = _safe_next_url(request, post_next or next_url, fallback_name="dashboard")

        form = BootstrapUserCreationForm(request.POST)  # tu form real
        if form.is_valid():
            user = form.save()

            # 🔒 Si quieres asignar group por intención, puedes hacerlo aquí
            # (si prefieres esperar al pago/invitación, muévelo al resume)
            role = intent.get("role")
            if role:
                _assign_user_group(user, role)

            # ✅ Login seguro con múltiples backends:
            raw_password = form.cleaned_data.get("password1")
            authed_user = authenticate(request, username=user.username, password=raw_password)

            if authed_user is not None:
                auth_login(request, authed_user)
            else:
                # Fallback: fuerza backend por defecto para evitar:
                # "You have multiple authentication backends..."
                backend_path = settings.AUTHENTICATION_BACKENDS[0]
                auth_login(request, user, backend=backend_path)

            # Aplicar invitación pendiente si existe (flujo de registro)
            try:
                _apply_pending_invitation(request, user)
            except Exception:
                pass

            # ✅ NO consumimos auth_intent aquí.
            # Lo dejamos en sesión para que profile_create lo use después.
            request.session["post_register_next"] = next_url

            # 👉 Siguiente paso obligatorio: completar Profile
            return redirect("authentication:profile_create")

        messages.error(request, "Por favor verifica los datos del formulario.")
        return render(request, "authentication/register.html", {"form": form, "next": next_url})

    # GET
    form = BootstrapUserCreationForm()
    return render(request, "authentication/register.html", {"form": form, "next": next_url})

def login_view(request):
    # Si ya está logueado, no tiene sentido mostrar login
    if request.user.is_authenticated:
        return redirect("dashboard")

    # next puede venir por querystring o por intent guardado en session
    query_next = request.GET.get("next")
    intent = request.session.get("auth_intent") or {}

    raw_next = intent.get("next") or query_next
    next_url = _safe_next_url(request, raw_next, fallback_name="dashboard")

    if request.method == "POST":
        # Si tu template manda <input hidden name="next">
        post_next = request.POST.get("next")
        next_url = _safe_next_url(request, post_next or next_url, fallback_name="dashboard")

        form = BootstrapAuthenticationForm(data=request.POST)  # <-- tu form actual
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # Aplicar invitación si existe
            invite_applied = False
            try:
                invite_applied = _apply_pending_invitation(request, user)
            except Exception:
                invite_applied = False

            # Limpieza de grupos duplicados si la tienes
            try:
                _normalize_student_groups(user)
            except Exception:
                pass

            # Consumimos intent AHORA (ya está logueado)
            intent = request.session.pop("auth_intent", {}) or {}
            source = intent.get("source")
            role = intent.get("role")
            item = intent.get("item") or {}
            legacy_course_id = intent.get("course_id")

            # Asignar grupo por rol (si es parte de tu estrategia)
            if role:
                _assign_user_group(user, role)

            # ---- Resolver intención ----
            # Classroom: delegar al flujo real
            if source == "classroom":
                if item.get("type") == "course" and item.get("id"):
                    return redirect("courses:start_course_payment", pk=item["id"])
                if legacy_course_id:
                    return redirect("courses:start_course_payment", pk=legacy_course_id)

            # Shop: normalmente vuelves al next (checkout/cart)
            if source == "shop":
                return redirect(next_url)

            # Invitación aplicada -> dashboard (o donde tú quieras)
            if invite_applied:
                return redirect("dashboard")

            # Default: next seguro
            return redirect(next_url)

        # Form inválido: NO redirijas (pierdes errores), renderiza la página
        messages.error(request, "Por favor verifica los datos del formulario.")
        return render(request, "authentication/login.html", {"form": form, "next": next_url})

    # GET
    form = BootstrapAuthenticationForm()
    return render(request, "authentication/login.html", {"form": form, "next": next_url})

def accounts_login_alias(request):
    """
    Evita bucles de /accounts/login/?next=/accounts/login...
    Redirige a la ruta real de login con next seguro si aplica.
    """
    query_next = request.GET.get("next")
    next_url = _safe_next_url(request, query_next, fallback_name="dashboard")
    if next_url == reverse("dashboard"):
        return redirect("authentication:login")
    return redirect(f"{reverse('authentication:login')}?next={next_url}")

def logout_view(request):
    auth_logout(request)   
    return redirect('shop:product_list')  # Redirect to login after logout

# CRUD de Profile

def _resolve_intent_redirect(request, fallback_name="dashboard"):
    """
    Consume el intent y decide a dónde seguir.
    OJO: aquí NO hacemos Enrollment. Solo redirigimos al flujo que lo hará.
    """
    intent = request.session.pop("auth_intent", None) or {}
    source = intent.get("source")
    item = intent.get("item") or {}
    legacy_course_id = intent.get("course_id")

    if source == "classroom":
        if item.get("type") == "course" and item.get("id"):
            return redirect("courses:start_course_payment", pk=item["id"])
        if legacy_course_id:
            return redirect("courses:start_course_payment", pk=legacy_course_id)

    if source == "shop":
        # si tienes un flujo específico, ponlo aquí
        # return redirect("checkout:checkout_list")
        raw_next = intent.get("next")
        return redirect(_safe_next_url(request, raw_next, fallback_name=fallback_name))

    if source == "invite":
        return redirect("dashboard")

    # por defecto, respetar next si existe
    raw_next = intent.get("next")
    if raw_next:
        return redirect(_safe_next_url(request, raw_next, fallback_name=fallback_name))

    # registro normal desde navbar: usa post_register_next si existe
    post_register_next = request.session.pop("post_register_next", None)
    if post_register_next:
        return redirect(_safe_next_url(request, post_register_next, fallback_name=fallback_name))

    return redirect(reverse(fallback_name))



@login_required
def profile_create_view(request):
    """
    Completa Profile. Si falta Address, redirige a address_create conservando next.
    Cuando Profile+Address están listos: consume auth_intent y redirige al flujo (classroom/shop/etc).
    """
    # Si ya existe profile para este user, no lo obligues a crearlo otra vez
    existing = Profiles.objects.filter(user=request.user).first()
    if existing:
        # si ya existe profile, entonces intenta resolver intent directo
        return _resolve_intent_redirect(request, fallback_name="dashboard")

    # next viene por querystring (si address_create te devuelve) o por intent
    query_next = request.GET.get("next")
    intent = request.session.get("auth_intent") or {}
    raw_next = query_next or intent.get("next")
    next_url = _safe_next_url(request, raw_next, fallback_name="dashboard")

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.old_cart = ""
            profile.save()

            # Asegurar Address residencial
            address = Address.objects.filter(user=request.user, address_type="residencial").first()

            if not address:
                # crea el registro base si no existe
                address = Address.objects.create(user=request.user, address_type="residencial")

            # si el profile no tiene direccion, asígnala
            if not getattr(profile, "direccion_id", None):
                profile.direccion = address
                profile.save(update_fields=["direccion"])

            # Si quieres obligar a completar detalles de address, manda al formulario
            # (Tu URL actual usa kwargs address_type y pk)
            addr_url = reverse(
                "authentication:address:address_create",
                kwargs={"address_type": "residencial", "pk": request.user.id},
            )

            # IMPORTANTÍSIMO:
            # NO consumas intent aquí si vas a mandar a address_create,
            # porque todavía falta completar address.
            # Le pasamos next para que address_create nos devuelva aquí.
            if not address or not getattr(address, "street", None):  # ajusta este check a tus campos reales
                return redirect(f"{addr_url}?next={reverse('authentication:profile_create')}")

            # ✅ Ya Profile + Address listos -> ahora sí consume intent y redirige
            return _resolve_intent_redirect(request, fallback_name="dashboard")

        messages.error(request, f"Por favor verifica los datos del formulario: {form.errors}")
        return render(request, "authentication/profile_create.html", {"form": form, "next": next_url})

    form = ProfileForm()
    return render(request, "authentication/profile_create.html", {"form": form, "next": next_url})

@login_required
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

@login_required
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

@login_required
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
            return redirect('shop:checkout:checkout_list')  # Redirect to the next stage
        else:
            messages.error(request, f'{form.errors} Error al crear el cliente. Por favor, corrige los errores.')
            return redirect('shop:checkout:checkout_list')
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
