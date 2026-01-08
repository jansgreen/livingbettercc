from .models import Module
from classroom.quicktest.models import QuickTest, QuickTestDefinition, QuickTestQuestion
from classroom.certifications.views import create_certificate_for_user

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from .models import Course, Module, Lesson
from .forms import CourseForm, ModuleForm, LessonForm
from classroom.enrollments.models import Enrollment, LessonCompletion
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from types import SimpleNamespace

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.decorators import login_required
from .models import Course
from authentication.models.students import Students  # Ajusta el import según tu estructura
from authentication.models.profiles import Profiles

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import Group
from classroom.courses.models import Course, Module, Lesson
from django.db.models import Prefetch



from types import SimpleNamespace
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from classroom.courses.models import Module
from classroom.quicktest.models import QuickTestDefinition, QuickTest
from classroom.enrollments.models import Enrollment, LessonCompletion


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
    """Permite a un usuario inscribirse en un curso."""
    if not request.user.is_authenticated:
        # Guardar intención en sesión para redirigir al curso después del registro
        request.session['post_register_role'] = 'student'
        request.session['selected_item'] = pk
        # Si viene un POST con datos de beca, guardarlos temporalmente en sesión
        if request.method == 'POST' and 'cedula' in request.POST:
            pending = {
                'cedula': request.POST.get('cedula', '').strip(),
                'exequatur': request.POST.get('exequatur', '').strip(),
                'centro_educativo': request.POST.get('centro_educativo', '').strip(),
                'distrito_escolar': request.POST.get('distrito_escolar', '').strip(),
                'street': request.POST.get('street', '').strip(),
                'neighborhood': request.POST.get('neighborhood', '').strip(),
                'provincia': request.POST.get('provincia', '').strip(),
                'municipio': request.POST.get('municipio', '').strip(),
                'zip_code': request.POST.get('zip_code', '').strip(),
                'city': request.POST.get('city', '').strip(),
                'state': request.POST.get('state', '').strip(),
            }
            request.session['pending_beca'] = pending
        messages.warning(request, 'Debes iniciar sesión o registrarte para inscribirte en un curso.')
        return redirect('authentication:register')

    user = request.user
    course = get_object_or_404(Course, pk=pk)

    # Crear o recuperar estudiante
    student, created = Students.objects.get_or_create(user=user)

    # Asegurarse de que el usuario pertenezca al grupo 'student'
    student_group, _ = Group.objects.get_or_create(name='student')
    if not user.groups.filter(name='student').exists():
        user.groups.add(student_group)

    # Verificar si el usuario tiene perfil
    profile = Profiles.objects.filter(user=user).first()

    # Si existe una solicitud de beca almacenada en sesión (usuario se autenticó luego), procesarla aquí
    pending_beca = request.session.get('pending_beca')
    if pending_beca:
        # Requiere perfil para beca Minerd
        if not profile:
            return redirect(reverse('authentication:profile_create'))
        cedula = pending_beca.get('cedula', '').strip()
        exequatur = pending_beca.get('exequatur', '').strip()
        centro_educativo = pending_beca.get('centro_educativo', '').strip()
        distrito_escolar = pending_beca.get('distrito_escolar', '').strip()
        street = pending_beca.get('street', '').strip()
        neighborhood = pending_beca.get('neighborhood', '').strip()
        provincia = pending_beca.get('provincia', '').strip()
        municipio = pending_beca.get('municipio', '').strip()
        zip_code = pending_beca.get('zip_code', '').strip()
        city = pending_beca.get('city', '').strip()
        state = pending_beca.get('state', '').strip()
        # Validación básica
        if not profile.profesion:
            messages.error(request, 'Debes tener una profesión registrada en tu perfil para aplicar a la beca Minerd.')
            return redirect('courses:course_detail', pk=pk)
        if not cedula or not exequatur or not centro_educativo or not distrito_escolar:
            messages.error(request, 'Debes completar todos los campos para aplicar a la beca Minerd.')
            return redirect('courses:course_detail', pk=pk)
        # Guardar datos en Students
        student.cedula = cedula
        student.certification = exequatur
        student.save()
        # Dirección laboral
        from authentication.address.models import Address
        address = Address.objects.create(
            user=user,
            address_type='laboral',
            street=street,
            neighborhood=neighborhood,
            city=city,
            state=state,
            zip_code=zip_code
        )
        # Guardar aplicación a beca
        from classroom.enrollments.models import BecaApplication
        beca_app, beca_created = BecaApplication.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'cedula': cedula,
                'exequatur': exequatur,
                'centro_educativo': centro_educativo,
                'distrito_escolar': distrito_escolar,
                'address': address,
                'status': 'submitted',
            }
        )
        if not beca_created:
            beca_app.cedula = cedula
            beca_app.exequatur = exequatur
            beca_app.centro_educativo = centro_educativo
            beca_app.distrito_escolar = distrito_escolar
            beca_app.address = address
            beca_app.status = 'submitted'
            beca_app.save()
        enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
        enrollment.status = Enrollment.Status.PENDING_APPROVAL
        enrollment.save()
        # Email de confirmación
        try:
            if user.email:
                EmailMessage(
                    subject='Solicitud de beca en revisión',
                    body=f'Hemos recibido tu solicitud de beca para {course.title}. Pronto te notificaremos el resultado.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                    to=[user.email],
                ).send(fail_silently=True)
        except Exception:
            pass
        # Limpiar sesión al completar
        request.session.pop('pending_beca', None)
        messages.success(request, f'Tu aplicación a la beca Minerd para {course.title} fue enviada y está en revisión.')
        return redirect('courses:my_course')

    # Si el usuario aplica a beca Minerd (POST con cedula y exequatur)
    if request.method == 'POST' and 'cedula' in request.POST and 'exequatur' in request.POST:
        # Requiere perfil para beca Minerd
        if not profile:
            return redirect(reverse('authentication:profile_create'))
        cedula = request.POST.get('cedula', '').strip()
        exequatur = request.POST.get('exequatur', '').strip()
        centro_educativo = request.POST.get('centro_educativo', '').strip()
        distrito_escolar = request.POST.get('distrito_escolar', '').strip()
        # Dirección laboral
        street = request.POST.get('street', '').strip()
        neighborhood = request.POST.get('neighborhood', '').strip()
        provincia = request.POST.get('provincia', '').strip()
        municipio = request.POST.get('municipio', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        # Validar profesional
        if not profile.profesion:
            messages.error(request, 'Debes tener una profesión registrada en tu perfil para aplicar a la beca Minerd.')
            return redirect('courses:course_detail', pk=pk)
        if not cedula or not exequatur or not centro_educativo or not distrito_escolar:
            messages.error(request, 'Debes completar todos los campos para aplicar a la beca Minerd.')
            return redirect('courses:course_detail', pk=pk)
        # Guardar datos en Students
        student.cedula = cedula
        student.certification = exequatur
        student.save()
        # Guardar dirección laboral
        from authentication.address.models import Address
        address = Address.objects.create(
            user=user,
            address_type='laboral',
            street=street,
            neighborhood=neighborhood,
            city=city,
            state=state,
            zip_code=zip_code
        )
        # Guardar aplicación a beca
        from classroom.enrollments.models import BecaApplication
        beca_app, beca_created = BecaApplication.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'cedula': cedula,
                'exequatur': exequatur,
                'centro_educativo': centro_educativo,
                'distrito_escolar': distrito_escolar,
                'address': address,
                'status': 'submitted',
            }
        )
        if not beca_created:
            beca_app.cedula = cedula
            beca_app.exequatur = exequatur
            beca_app.centro_educativo = centro_educativo
            beca_app.distrito_escolar = distrito_escolar
            beca_app.address = address
            beca_app.status = 'submitted'
            beca_app.save()
        # Crear o recuperar matrícula y marcar estado pendiente de aprobación
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        enrollment.status = Enrollment.Status.PENDING_APPROVAL
        enrollment.save()
        if created:
            messages.success(request, f'Tu aplicación a la beca Minerd para {course.title} fue enviada y está en revisión.')
        else:
            messages.info(request, f'Tu matrícula está en revisión para la beca.')
        # Email de confirmación de solicitud en revisión
        try:
            if user.email:
                EmailMessage(
                    subject='Solicitud de beca en revisión',
                    body=f'Hemos recibido tu solicitud de beca para {course.title}. Pronto te notificaremos el resultado.',
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER),
                    to=[user.email],
                ).send(fail_silently=True)
        except Exception:
            pass
        return redirect('courses:my_course')

    # Inscripción normal (pago)
    enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
    if course.price and float(course.price) > 0:
        enrollment.status = Enrollment.Status.PENDING_PAYMENT
        enrollment.save()
        msg = f'Registrado en {course.title}. Completa el pago para activar tu acceso.'
    else:
        enrollment.status = Enrollment.Status.ACTIVE
        enrollment.save()
        msg = f'Te has matriculado con éxito en {course.title}.'
    messages.success(request, msg if created else f'Ya estás matriculado en {course.title}.')

    return redirect('courses:my_course')

def course_list(request):
    can_access_module = request.user.has_perm('groups.access_module')
    courses = Course.objects.filter(published=True)
    context = {
        'courses': courses,
        'can_access_module': can_access_module,
    }
    return render(request, 'courses/course_list.html', context)

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

    # For paid courses, even a newly created enrollment should go to pending_payment
    if course.price and float(course.price) > 0:
        if enrollment.status != Enrollment.Status.COMPLETED:
            if enrollment.status != Enrollment.Status.PENDING_PAYMENT:
                enrollment.status = Enrollment.Status.PENDING_PAYMENT
                enrollment.save(update_fields=['status'])
            return redirect(reverse('enrollments:create_checkout_session', kwargs={'enrollment_id': enrollment.id}))
        # Completed remains as-is
        return redirect('courses:my_course')

    # Free courses:
    if enrollment.status in (Enrollment.Status.ACTIVE, Enrollment.Status.COMPLETED):
        return redirect('courses:my_course')

    if enrollment.status == Enrollment.Status.PENDING_APPROVAL:
        messages.info(request, 'Tu matrícula está en revisión (beca).')
        return redirect('courses:my_course')

    # Free course: activate and go to my_course
    enrollment.status = Enrollment.Status.ACTIVE
    enrollment.save(update_fields=['status'])
    return redirect('courses:my_course')

@login_required
def my_course(request):
    enrollments = Enrollment.objects.filter(user=request.user, completed=False)

    # Cursos con módulos y lessons prefetcheados (clave para que module.status exista en template)
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

    # Lessons completadas
    completed_ids = LessonCompletion.objects.filter(
        enrollment__in=enrollments,
        lesson__module__course__in=course_ids
    ).values_list('lesson_id', flat=True)

    completed_set = set(completed_ids)

    # Lista única de módulos desde courses (sin queries extra y sin instancias distintas)
    modules = []
    for c in courses:
        modules.extend(list(c.modules.all()))

    # Status por módulo
    module_status = {}
    for m in modules:
        lessons = list(m.lessons.all())  # ya prefetcheado
        total = len(lessons)
        done = sum(1 for l in lessons if l.id in completed_set)
        is_completed = total > 0 and done >= total

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
            "completed_ids": list(completed_ids),
            'has_quicktest': has_quicktest,
            'questions_total': questions_total,
            'score': score,
            'passed': passed,
        }

        # Para template: module.status
        m.status = module_status[m.id]

    # Asegura que course.modules.all() también tenga status (usa mismos objetos del prefetch)
    for c in courses:
        for m in c.modules.all():
            m.status = module_status.get(m.id)

    context = {
        'enrollments': enrollments,
        'courses': courses,
        'modules': modules,
        'completed_ids': completed_ids,
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
        form = LessonForm(request.POST)

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
        form = LessonForm(request.POST, instance=lesson)
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

    enrollments = Enrollment.objects.filter(user=request.user, completed=False)

    courses = (
        Course.objects
        .filter(enrollment__in=enrollments)
        .distinct()
        .prefetch_related(
            Prefetch("modules", queryset=Module.objects.prefetch_related("lessons"))
        )
    )
    modules = Module.objects.filter(course__in=courses).distinct().prefetch_related("lessons")

    context = {
        'lesson': lesson,
    }
    return render(request, 'lesson/lesson_detail.html', context)

@login_required
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully.')
        return redirect('courses:module_list')
    else:
        messages.error(request, 'Error deleting lesson.')
        return redirect('courses:module_list')


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

@login_required
def next_module(request, module_id):
    module = get_object_or_404(Module, pk=module_id)
    course = module.course
    # Si el módulo actual tiene quicktest, verificar que el usuario haya aprobado (>=70)
    if QuickTestDefinition.objects.filter(module=module).exists():
        qt = QuickTest.objects.filter(user=request.user, module=module).order_by('-completed_at').first()
        if not qt or float(qt.score) < 70:
            messages.info(request, 'Debes aprobar el test de este módulo antes de continuar.')
            return redirect('courses:module_detail', pk=module.pk)
    next_mod = Module.objects.filter(course=course, order__gt=module.order).order_by('order').first()
    if next_mod:
        return redirect('courses:module_detail', pk=next_mod.pk)
    else:
        # El usuario ha completado todos los módulos del curso
        # Marcar la matrícula como completada
        enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
        if enrollment:
            enrollment.completed = True
            enrollment.save()
        create_certificate_for_user(request.user, course)
        messages.success(request, '¡Has completado todos los módulos de este curso! Se ha generado tu certificado.')
        return redirect('courses:my_course')





