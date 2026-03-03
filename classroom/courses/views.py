from classroom.certifications.models import Certificate
from .models import Module
from classroom.quicktest.models import QuickTest, QuickTestDefinition, QuickTestQuestion
from classroom.certifications.views import create_certificate_for_user
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from .forms import CourseForm, ModuleForm, LessonForm
from classroom.enrollments.models import Enrollment, LessonCompletion
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from types import SimpleNamespace
import json
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from authentication.models.students import Students  # Ajusta el import según tu estructura
from authentication.models.profiles import Profiles
from django.contrib.auth.models import Group
from classroom.courses.models import Course, Module, Lesson
from django.db.models import Prefetch, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from classroom.enrollments.models import Enrollment, ModuleCompletion
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.db import transaction

def _require_active_enrollment(request, *, course):
    enr = Enrollment.objects.filter(
        user=request.user,
        course=course,
    ).order_by('-id').first()
    if not enr:
        messages.error(request, "Debes inscribirte para acceder al contenido de este curso.")
        return None, redirect("courses:course_detail", pk=course.pk)
    if enr.status != Enrollment.Status.ACTIVE:
        messages.warning(request, "Debes realizar el pago para acceder a las lecciones.")
        return enr, redirect("courses:course_detail", pk=course.pk)
    return enr, None


def _require_staff(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        raise Http404("No encontrado")
    return None

from classroom.courses.models import Module
from classroom.enrollments.models import Enrollment, LessonCompletion, ModuleCompletion
from classroom.quicktest.models import QuickTest, QuickTestDefinition
from classroom.certifications.models import Certificate
from django.utils.http import url_has_allowed_host_and_scheme



# incribiendo el nuevo estudiants

def session_enroll_students(request, pk):
    # Si NO está autenticado: guarda intención y manda a register
    if not request.user.is_authenticated:
        next_url = request.get_full_path()

        # Seguridad: evita next a dominios externos o urls raras
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = "/"

        # Unificamos formato de auth_intent para que login/profile resuelvan igual
        request.session["auth_intent"] = {
            "source": "classroom",
            "role": "estudiantes",
            "item": {"type": "course", "id": pk},
            "next": next_url,
        }

        return redirect("authentication:register")

    # Si YA está autenticado: sigue el flujo normal
    return redirect("courses:start_course_payment", pk=pk)

@login_required
def quicktest_view(request, module_id):
    module = get_object_or_404(Module, pk=module_id)

    qdef = QuickTestDefinition.objects.filter(module=module).first()
    if not qdef:
        messages.error(request, 'Este módulo no tiene quicktest asignado.')
        return redirect('courses:module_detail', pk=module_id)

    # Gate: require all lessons completed before allowing the quicktest
    enr = Enrollment.objects.filter(user=request.user, course=module.course).order_by('-id').first()
    total_lessons = module.lessons.count()
    completed_count = 0
    if enr and total_lessons:
        completed_count = LessonCompletion.objects.filter(
            enrollment=enr,
            lesson__module=module
        ).count()

    if total_lessons and completed_count < total_lessons:
        messages.info(request, 'Debes completar todas las lecciones del módulo antes de tomar el test.')
        return redirect('courses:module_detail', pk=module_id)

    # Proxy para mantener tu template actual "test.questions.all"
    class _QWrap:
        def __init__(self, qs):
            self._qs = qs
        def all(self):
            return self._qs
        def count(self):
            return self._qs.count()

    questions_qs = qdef.questions.all()
    test_proxy = SimpleNamespace(questions=_QWrap(questions_qs))

    # POST: evaluar y mostrar resultados (NO redirect inmediato)
    if request.method == 'POST':
        correct = 0
        total = questions_qs.count()

        for q in questions_qs:
            user_answer = request.POST.get(f'question_{q.id}')
            if user_answer == q.correct_option:
                correct += 1

        score = (correct / total) * 100 if total > 0 else 0
        passed = score >= 70

        QuickTest.objects.update_or_create(
            user=request.user,
            module=module,
            defaults={'score': score}
        )

        context = {
            'module': module,
            'test': test_proxy,
            'result': {
                'score': round(score, 2),
                'passed': passed,
                'correct': correct,
                'total': total,
            },
            # Botones útiles
            'back_to_course_url': reverse('courses:my_course'),
            'retry_url': reverse('courses:quicktest', kwargs={'module_id': module_id}),
            'next_url': reverse('courses:next_module', kwargs={'module_id': module_id}),
        }
        return render(request, 'courses/quicktest.html', context)

    # GET: mostrar preguntas
    return render(request, 'courses/quicktest.html', {
        'module': module,
        'test': test_proxy,
        'back_to_course_url': reverse('courses:my_course'),
    })

def course_enroll(request, pk):
    """Legacy endpoint: redirect to the modern auth_intent flow."""
    return redirect("courses:session_enroll_students", pk=pk)

def course_list(request):
    can_access_module = request.user.has_perm('groups.access_module')
    modules_prefetch = Prefetch(
        "modules",
        queryset=Module.objects.prefetch_related(
            Prefetch("lessons", queryset=Lesson.objects.order_by("order", "id"))
        ).order_by("order", "id"),
    )
    if request.user.is_staff or request.user.is_superuser or can_access_module:
        courses = (
            Course.objects
            .all()
            .annotate(modules_count=Count("modules", distinct=True))
            .annotate(lessons_count=Count("modules__lessons", distinct=True))
            .prefetch_related(modules_prefetch)
        )
    else:
        courses = (
            Course.objects
            .filter(published=True)
            .annotate(modules_count=Count("modules", distinct=True))
            .annotate(lessons_count=Count("modules__lessons", distinct=True))
            .prefetch_related(modules_prefetch)
        )
    context = {
        'courses': courses,
        'can_access_module': can_access_module,
    }
    return render(request, 'courses/course_list.html', context)


@login_required
def course_admin_list(request):
    _require_staff(request)
    courses = Course.objects.all().order_by('title')
    return render(request, 'courses/admin_course_list.html', {'courses': courses})


@login_required
def course_admin_detail(request, pk):
    _require_staff(request)
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons'),
        pk=pk
    )
    return render(request, 'courses/admin_course_detail.html', {'course': course})

def course_detail(request, pk):
    course = Course.objects.prefetch_related('modules__lessons').get(pk=pk)

    is_enrolled = False
    beca_status = None
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).first()
        # Consultar estado de beca Minerd para este curso
        from classroom.enrollments.models import BecaApplication
        beca_app = BecaApplication.objects.filter(user=request.user, course=course).order_by('-fecha_aplicacion').first()
        if beca_app:
            beca_status = beca_app.status
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'beca_status': beca_status,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def start_course_payment(request, pk):
    """
    Allow user to pay immediately from course detail.
    - Ensures profile if required, redirecting to profile creation with next.
    - get_or_create Enrollment(user, course)
    - If ACTIVE/COMPLETED -> redirect my_course
    - If PENDING_APPROVAL -> redirect my_course with message
    - Else set PENDING_PAYMENT for paid courses and delegate to enrollments:create_checkout_session
    """
    course = get_object_or_404(Course, pk=pk)

    # Optional profile requirement: if project requires a Profile to proceed with payment
    try:
        from authentication.models.profiles import Profiles
        profile = Profiles.objects.filter(user=request.user).first()
    except Exception:
        profile = None

    if not profile:
        # Redirect to profile create with next back to this pay route
        next_url = request.get_full_path()
        return redirect(f"{reverse('authentication:profile_create')}?next={next_url}")

    enrollment, created = Enrollment.objects.get_or_create(user=request.user, course=course)

    # Treat any course with a positive price as paid, even if payment_required was left unchecked.
    is_paid_course = bool(course.payment_required or (course.price and course.price > 0))

    # For paid courses, even a newly created enrollment should go to pending_payment
    if not is_paid_course:
        # Curso gratis: activar inscripción y redirigir a mis cursos
        enrollment.status = Enrollment.Status.ACTIVE
        enrollment.save(update_fields=['status'])
        return redirect('courses:my_course')
    else:
        # Curso de pago: marcar pendiente de pago y redirigir a checkout
        if enrollment.status != Enrollment.Status.COMPLETED:
            if enrollment.status != Enrollment.Status.PENDING_PAYMENT:
                enrollment.status = Enrollment.Status.PENDING_PAYMENT
                enrollment.save(update_fields=['status'])
            return redirect(reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': enrollment.id}))
        # Si ya está completado, solo redirige

    if enrollment.status == Enrollment.Status.PENDING_APPROVAL:
        messages.info(request, 'Tu matrícula está en revisión (beca).')
        return redirect('courses:my_course')

    # Free course: activate and go to my_course
    enrollment.status = Enrollment.Status.ACTIVE
    enrollment.save(update_fields=['status'])
    return redirect('courses:my_course')

@login_required
def my_course(request):
    enrollments = Enrollment.objects.filter(
        user=request.user,
        completed=False,
    ).exclude(status__in=[Enrollment.Status.REJECTED, Enrollment.Status.CANCELLED])

    courses = (
        Course.objects
        .filter(enrollment__in=enrollments)
        .distinct()
        .prefetch_related(
            Prefetch("modules", queryset=Module.objects.prefetch_related("lessons"))
        )
    )

    course_ids = [c.id for c in courses]

    # Fallback de imagen
    for c in courses:
        try:
            _ = c.image.url
        except Exception:
            c.image = SimpleNamespace(url='https://via.placeholder.com/48x38')

    # Pago pendiente
    pending = next((e for e in enrollments if e.status == Enrollment.Status.PENDING_PAYMENT), None)
    if pending:
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': pending.id})
        messages.info(request, f"Pago pendiente | {pay_url}")

    # Lessons completadas (IMPORTANTE: conviértelo a LISTA UNA VEZ)
    completed_ids_qs = LessonCompletion.objects.filter(
        enrollment__in=enrollments,
        lesson__module__course__in=course_ids
    ).values_list('lesson_id', flat=True)

    completed_ids = list(completed_ids_qs)   # ✅ lista real para el template
    completed_set = set(completed_ids)       # ✅ set para cálculos rápidos en Python

    # Lista única de módulos desde courses (usa mismos objetos del prefetch)
    modules = []
    for c in courses:
        modules.extend(list(c.modules.all()))

    module_status = {}
    for m in modules:
        lessons = list(m.lessons.all())  # ya prefetcheado + ordenado por Meta ordering
        total = len(lessons)
        done = sum(1 for l in lessons if l.id in completed_set)
        is_completed = total > 0 and done >= total

        # ✅ next_lesson_id: si no hay completadas, la primera siempre se habilita
        if total == 0:
            next_lesson_id = None
        elif done == 0:
            next_lesson_id = lessons[0].id
        else:
            next_lesson_id = next((l.id for l in lessons if l.id not in completed_set), None)

        qdef = QuickTestDefinition.objects.filter(module=m).first()
        has_quicktest = bool(qdef)
        questions_total = qdef.questions.count() if qdef else 0

        qt = QuickTest.objects.filter(user=request.user, module=m).order_by('-completed_at').first()
        score = float(qt.score) if qt else None
        passed = (score is not None) and (score >= 70)

        module_status[m.id] = {
            'lessons_total': total,
            'lessons_completed': done,
            'is_completed': is_completed,
            'next_lesson_id': next_lesson_id,   # ✅ clave para habilitar la primera / siguiente
            'has_quicktest': has_quicktest,
            'questions_total': questions_total,
            'score': score,
            'passed': passed,
        }

        # Para template: module.status
        m.status = module_status[m.id]

    # Asegura status dentro de course.modules.all()
    for c in courses:
        for m in c.modules.all():
            m.status = module_status.get(m.id)

    context = {
        'enrollments': enrollments,
        'courses': courses,
        'modules': modules,
        'completed_ids': completed_ids,   # ✅ lista
        'module_status': module_status,
        'has_active': any(e.status == Enrollment.Status.ACTIVE for e in enrollments),
    }

    resp = render(request, 'courses/my_course.html', context)

    if pending:
        html = resp.content.decode('utf-8', errors='ignore')
        pay_url = reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': pending.id})
        insertion = f"\n<div>Pago pendiente</div>\n<a href=\"{pay_url}\"></a>\n"
        html = html.replace('</main>', insertion + '</main>')
        return HttpResponse(html)

    return resp


@login_required
def course_unenroll(request, pk):
    if request.method != "POST":
        return redirect("courses:my_course")

    enrollment = Enrollment.objects.filter(user=request.user, course_id=pk).first()
    if not enrollment:
        messages.error(request, "No encontramos una inscripcion activa para ese curso.")
        return redirect("courses:my_course")

    if enrollment.status == Enrollment.Status.COMPLETED or enrollment.completed:
        messages.warning(request, "No puedes darte de baja de un curso ya completado.")
        return redirect("courses:my_course")

    enrollment.status = Enrollment.Status.CANCELLED
    enrollment.completed = False
    enrollment.save(update_fields=["status", "completed"])

    messages.success(
        request,
        "Te has dado de baja del curso. El monto pagado quedara como credito para futuros cursos."
    )
    return redirect("courses:my_course")

@login_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('courses:course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

@login_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('courses:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'object': course})

@login_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully.')
        return redirect('courses:course_list')
    context = {
        'object': course,
        'course': course,
    }
    return render(request, 'courses/course_confirm_delete.html', context)

# modules funciones
@login_required
def module_create(request):
    form = ModuleForm()
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            course_id = request.POST.get('course')
            module.course = get_object_or_404(Course, pk=course_id)
            module.save()
            messages.success(request, 'Module created successfully.')
            return redirect('courses:module_create') #return redirect('courses:course-detail', pk=module.course.pk)
        else:
            messages.error(request, 'Error creating module. Please correct the errors below.')
            return redirect('courses:module_create')
    context = {
        'form': form,
        'courses': Course.objects.all()
    }
    return render(request, 'module/module_form.html', context)

@login_required
def module_list(request):
    modules = Module.objects.all()
    lessons = Lesson.objects.filter(module__in=modules)
    context = {
        'modules': modules,
        'lessons': lessons,
    }
    return render(request, 'module/module_list.html', context)

@login_required
def module_update(request, pk):
    module = get_object_or_404(Module, pk=pk)
    form = ModuleForm(instance=module)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully.')
            return redirect('courses:module_list')
        else:
            messages.error(request, 'Error updating module. Please correct the errors below.')
            return redirect('courses:module_update', pk=pk)
    context = {
        'form': form,
        'courses': Course.objects.all(),
        'module': module,
        'object': True,
    }
    return render(request, 'module/module_form.html', context)

@login_required
def module_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    lessons = module.lessons.all()
    quicktest_result = None
    has_qdef = QuickTestDefinition.objects.filter(module=module).exists()
    if has_qdef:
        qdef = QuickTestDefinition.objects.get(module=module)
        class _QWrap:
            def __init__(self, qs):
                self._qs = qs
            def all(self):
                return self._qs
            def count(self):
                return self._qs.count()
        module.test = SimpleNamespace(questions=_QWrap(qdef.questions.all()))

    if request.user.is_authenticated and has_qdef:
        qt = QuickTest.objects.filter(user=request.user, module=module).order_by('-completed_at').first()
        if qt:
            passed = float(qt.score) >= 70
            quicktest_result = SimpleNamespace(score=float(qt.score), passed=passed)
    context = {
        'module': module,
        'lessons': lessons,
        'quicktest_result': quicktest_result,
        'has_quicktest': has_qdef,
    }
    return render(request, 'module/module_detail.html', context)

@login_required
def module_delete(request, pk):
    module = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully.')
        return redirect('courses:module_list')
    context = {
        'module': module,
    }
    return render(request, 'module/module_confirm_delete.html', context)

# 🔹 Lecciones funciones
@login_required
def lesson_list(request):
    lessons = Lesson.objects.all()
    context = {
        'lessons': lessons,
    }
    return render(request, 'lesson/lesson_list.html', context)

@login_required
def lesson_create(request):
    form = LessonForm()
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)

        if form.is_valid():
            lesson = form.save(commit=False)
            module_id = request.POST.get('module')
            lesson.module = get_object_or_404(Module, pk=module_id)
            lesson.save()

            messages.success(request, 'Lesson created successfully.')
            return redirect('courses:module_list')
        else:
            messages.error(request, 'Error creating lesson. Please correct the errors below.')
            return redirect('courses:lesson_create')
    context = {
        'form': form,
        'courses': Course.objects.all(),
        'object': False,  # Indica que no es una edición
    }
    return render(request, 'lesson/lesson_form.html', context)

@login_required
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST': #A
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully.')
            return redirect('courses:module_list')
    else:
        form = LessonForm(instance=lesson)
    context = {
        'form': form,
        'lesson': lesson,
        'object': True,
    }
    return render(request, 'lesson/lesson_form.html', context)

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    module = lesson.module
    course = module.course

    enr = Enrollment.objects.filter(
        user=request.user,
        course=course,
        status=Enrollment.Status.ACTIVE,
        completed=False
    ).first()

    if not enr:
        messages.error(request, "No tienes acceso a este curso (inscripción inactiva o pendiente).")
        return redirect("courses:my_course")

    # Orden real de lessons (usa Meta ordering + id para estabilidad)
    ordered_lessons = list(module.lessons.order_by("order", "id"))

    # Index de la lección actual
    try:
        idx = next(i for i, l in enumerate(ordered_lessons) if l.id == lesson.id)
    except StopIteration:
        messages.error(request, "Lección inválida para este módulo.")
        return redirect("courses:my_course")

    # Todas las previas deben estar completadas
    prev_lessons = ordered_lessons[:idx]
    prev_ids = [l.id for l in prev_lessons]

    if prev_ids:
        completed_prev_ids = set(
            LessonCompletion.objects.filter(
                enrollment=enr,
                lesson_id__in=prev_ids
            ).values_list("lesson_id", flat=True)
        )

        if len(completed_prev_ids) < len(prev_ids):
            # primera pendiente (en el orden real)
            first_pending = next((l for l in prev_lessons if l.id not in completed_prev_ids), None)

            messages.warning(request, "Debes completar las lecciones en orden.")
            if first_pending:
                return redirect("courses:lesson_detail", pk=first_pending.id)
            return redirect("courses:my_course")

    return render(request, "lesson/lesson_detail.html", {"lesson": lesson})

@login_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    lesson.delete()
    return redirect('courses:lesson_list')

# guarda los resultados del test 
@csrf_exempt
@login_required
def save_test_result(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        module_id = data.get('module_id')
        score = data.get('score')

        module = Module.objects.get(pk=module_id)
        user = request.user

        # Guarda/actualiza resultado en quicktest anidado
        QuickTest.objects.update_or_create(
            user=user,
            module=module,
            defaults={'score': score}
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
@login_required
def test_detail(request, pk):
    module = get_object_or_404(Module, pk=pk)
    # Deprecated: handled by quicktest_view; keep redirect
    if request.method == 'POST':
        data = json.loads(request.body)
        score = data.get('score')
        # Aquí podrías guardar el resultado del test si es necesario
        return JsonResponse({'status': 'success', 'score': score})

    # Deprecated: no dedicated template; redirect to quicktest
    return redirect('courses:quicktest', module_id=module.pk)


PASSING_SCORE = 70

def _module_lessons_completed(*, enrollment: Enrollment, module: Module) -> bool:
    lesson_ids = list(module.lessons.values_list("id", flat=True))
    if not lesson_ids:
        return True  # módulo sin lecciones => lo tratamos como completo
    done = LessonCompletion.objects.filter(enrollment=enrollment, lesson_id__in=lesson_ids).count()
    return done >= len(lesson_ids)

def _passed_quicktest(user, module) -> bool:
    """True if module has no test OR user has latest score >= PASSING_SCORE."""
    has_qdef = QuickTestDefinition.objects.filter(module=module).exists()
    if not has_qdef:
        return True
    qt = QuickTest.objects.filter(user=user, module=module).order_by("-completed_at").first()
    return bool(qt and float(qt.score) >= PASSING_SCORE)

@login_required
def next_module(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    course = module.course

    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        messages.error(request, "No estás inscrito en este curso.")
        return redirect("courses:course_list")

    if enrollment.status != Enrollment.Status.ACTIVE:
        messages.error(request, "Debes completar el pago o esperar aprobación para avanzar en el curso.")
        return redirect("courses:my_course")

    # 1) Exigir aprobar test del módulo actual (si existe)
    if not _passed_quicktest(request.user, module):
        messages.info(request, "Debes aprobar el test de este módulo antes de continuar.")
        return redirect("courses:module_detail", pk=module.pk)

    # 2) Marcar el módulo como completado (idempotente)
    ModuleCompletion.objects.get_or_create(enrollment=enrollment, module=module)

    # 3) Calcular progreso del curso basado en módulos completados
    total_modules = course.modules.count()
    completed_modules = ModuleCompletion.objects.filter(enrollment=enrollment).count()
    progress = (completed_modules / total_modules) * 100 if total_modules else 0
    enrollment.progress = round(progress, 2)
    enrollment.save(update_fields=["progress"])

    # 4) Encontrar siguiente módulo de forma robusta
    modules = list(course.modules.all().order_by("order", "id"))
    try:
        idx = next(i for i, m in enumerate(modules) if m.id == module.id)
    except StopIteration:
        messages.error(request, "Módulo inválido.")
        return redirect("courses:my_course")

    next_mod = modules[idx + 1] if (idx + 1) < len(modules) else None
    if next_mod:
        return redirect("courses:module_detail", pk=next_mod.pk)

    # ======= ÚLTIMO MÓDULO: VALIDAR TODO Y FINALIZAR =======

    # 5a) Todas las lecciones del curso completas
    total_lessons = Lesson.objects.filter(module__course=course).count()
    completed_lessons = LessonCompletion.objects.filter(enrollment=enrollment).count()
    if completed_lessons < total_lessons:
        messages.warning(request, "Aún te faltan lecciones por completar antes de finalizar el curso.")
        return redirect("courses:my_course")

    # 5b) Todos los quicktests aprobados (para módulos que tengan test)
    not_passed = [m for m in modules if not _passed_quicktest(request.user, m)]
    if not_passed:
        messages.warning(request, "Te falta aprobar al menos un test antes de finalizar el curso.")
        return redirect("courses:module_detail", pk=not_passed[0].pk)

    # 6) Finalizar enrollment + generar certificado (atómico)
    with transaction.atomic():
        enrollment.completed = True
        enrollment.status = Enrollment.Status.COMPLETED
        enrollment.progress = 100
        enrollment.save(update_fields=["completed", "status", "progress"])

        cert, _ = Certificate.objects.get_or_create(user=request.user, course=course)
        cert.save()  # genera cert_no si faltaba

    messages.success(request, "¡Curso completado! Tu certificado está disponible.")
    return redirect("certifications:my_certificate_detail", uuid=cert.uuid)
