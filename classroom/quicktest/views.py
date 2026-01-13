from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from classroom.courses.models import Module
from .models import QuickTest, QuickTestDefinition, QuickTestQuestion
from .forms import QuickTestDefinitionForm, QuickTestQuestionForm

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from classroom.courses.models import Module
from classroom.enrollments.models import Enrollment
from .models import QuickTest, QuickTestDefinition

@login_required
def quicktest_list(request):
    tests = QuickTest.objects.filter(user=request.user)
    return render(request, 'quicktest/quicktest_list.html', {'tests': tests})

@login_required
def quicktest_detail(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    return render(request, 'quicktest/quicktest_detail.html', {'test': test})


from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from classroom.courses.models import Module
from classroom.enrollments.models import Enrollment, LessonCompletion
from classroom.quicktest.models import QuickTest, QuickTestDefinition

PASSING_SCORE = 70


@login_required
def quicktest_taking(request, module_id):
    module = get_object_or_404(Module, pk=module_id)

    # 1) Debe estar inscrito y ACTIVE
    enrollment = (
        Enrollment.objects.filter(user=request.user, course=module.course)
        .order_by("-id")
        .first()
    )
    if not enrollment:
        messages.error(request, "No estás inscrito en este curso.")
        return redirect("courses:course_detail", pk=module.course_id)

    if enrollment.status != Enrollment.Status.ACTIVE:
        messages.error(request, "Debes completar el pago o esperar aprobación para tomar el test.")
        return redirect("courses:my_course")

    # 2) Debe existir QuickTestDefinition
    qdef = QuickTestDefinition.objects.filter(module=module).first()
    if not qdef:
        messages.info(request, "Este módulo no tiene test. Puedes continuar.")
        return redirect("courses:next_module", module_id=module.id)

    # 3) Gate: exigir lecciones del módulo completadas antes del test
    total_lessons = module.lessons.count()
    if total_lessons:
        completed_lessons = LessonCompletion.objects.filter(
            enrollment=enrollment,
            lesson__module=module
        ).count()
        if completed_lessons < total_lessons:
            messages.info(request, "Debes completar todas las lecciones del módulo antes de tomar el test.")
            return redirect("courses:module_detail", pk=module.id)

    # Proxy para que tu template use: test.questions.all y test.questions.count
    class _QWrap:
        def __init__(self, qs):
            self._qs = qs
        def all(self):
            return self._qs
        def count(self):
            return self._qs.count()

    questions_qs = qdef.questions.all()
    test_proxy = SimpleNamespace(questions=_QWrap(questions_qs))

    # Context base (MISMAS KEYS que quicktest_view)
    base_context = {
        "module": module,
        "test": test_proxy,
        "back_to_course_url": reverse("courses:my_course"),
        "retry_url": reverse("quicktest:quicktest_taking", kwargs={"module_id": module.id}),
        "next_url": reverse("courses:next_module", kwargs={"module_id": module.id}),
    }

    # 4) GET: muestra preguntas
    if request.method != "POST":
        return render(request, "courses/quicktest.html", base_context)

    # 5) POST: evaluar respuestas
    total = questions_qs.count()
    correct = 0

    for q in questions_qs:
        user_answer = request.POST.get(f"question_{q.id}")
        if user_answer == q.correct_option:
            correct += 1

    score = (correct / total) * 100 if total > 0 else 0
    passed = score >= PASSING_SCORE

    # Guardar / actualizar resultado (una fila por user+module)
    QuickTest.objects.update_or_create(
        user=request.user,
        module=module,
        defaults={"score": round(score, 2)},
    )

    # Armar result para el template
    context = {
        **base_context,
        "result": {
            "score": round(score, 2),
            "passed": passed,
            "correct": correct,
            "total": total,
            "passing_score": PASSING_SCORE,
        }
    }

    # 6) Si pasa -> redirigir a next_module (ahí se marca módulo y finaliza curso + certificado)
    if passed:
        messages.success(request, "✅ Test aprobado. Continuando...")
        return redirect("courses:next_module", module_id=module.id)

    # Si no pasa -> reintentar (mantenemos UI, y NO mostramos next_url)
    messages.warning(request, f"❌ No aprobaste (mínimo {PASSING_SCORE}). Intenta de nuevo.")
    context["next_url"] = None
    return render(request, "courses/quicktest.html", context)

@login_required
def quicktest_update(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    if request.method == 'POST':
        score = request.POST.get('score')
        test.score = score
        test.save()
        return redirect('quicktest_detail', pk=test.pk)
    return render(request, 'quicktest/quicktest_form.html', {'test': test})

@login_required
def quicktest_delete(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    if request.method == 'POST':
        test.delete()
        return redirect('quicktest_list')
    return render(request, 'quicktest/quicktest_confirm_delete.html', {'test': test})


# --------------------------
# Staff CRUD for QuickTests
# --------------------------

def _ensure_staff(request):
    if not request.user.is_authenticated:
        return False
    return request.user.is_staff or request.user.is_superuser

@login_required
def qdef_list(request):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    defs = QuickTestDefinition.objects.select_related('module', 'module__course').order_by('module__course__title', 'module__order')
    return render(request, 'quicktest/qdef_list.html', {'definitions': defs})

@login_required
def qdef_create(request):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    if request.method == 'POST':
        form = QuickTestDefinitionForm(request.POST)
        if form.is_valid():
            qdef = form.save()
            messages.success(request, 'QuickTest creado.')
            return redirect('quicktest:qdef_list')
    else:
        form = QuickTestDefinitionForm()
    return render(request, 'quicktest/qdef_form.html', {'form': form})

@login_required
def qdef_update(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=pk)
    if request.method == 'POST':
        form = QuickTestDefinitionForm(request.POST, instance=qdef)
        if form.is_valid():
            form.save()
            messages.success(request, 'QuickTest actualizado.')
            return redirect('quicktest:qdef_list')
    else:
        form = QuickTestDefinitionForm(instance=qdef)
    return render(request, 'quicktest/qdef_form.html', {'form': form, 'qdef': qdef})

@login_required
def qdef_delete(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=pk)
    if request.method == 'POST':
        qdef.delete()
        messages.success(request, 'QuickTest eliminado.')
        return redirect('quicktest:qdef_list')
    return render(request, 'quicktest/qdef_confirm_delete.html', {'qdef': qdef})

@login_required
def q_list(request, def_id):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    qs = qdef.questions.all()
    return render(request, 'quicktest/q_list.html', {'qdef': qdef, 'questions': qs})

@login_required
def q_create(request, def_id):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    if request.method == 'POST':
        form = QuickTestQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.definition = qdef
            q.save()
            messages.success(request, 'Pregunta creada.')
            return redirect('quicktest:q_list', def_id=qdef.id)
    else:
        form = QuickTestQuestionForm()
    return render(request, 'quicktest/q_form.html', {'form': form, 'qdef': qdef})

@login_required
def q_update(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    q = get_object_or_404(QuickTestQuestion, pk=pk)
    if request.method == 'POST':
        form = QuickTestQuestionForm(request.POST, instance=q)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pregunta actualizada.')
            return redirect('quicktest:q_list', def_id=q.definition_id)
    else:
        form = QuickTestQuestionForm(instance=q)
    return render(request, 'quicktest/q_form.html', {'form': form, 'qdef': q.definition, 'question': q})

@login_required
def q_delete(request, pk):
    if not _ensure_staff(request):
        messages.error(request, 'No autorizado.')
        return redirect('/')
    q = get_object_or_404(QuickTestQuestion, pk=pk)
    if request.method == 'POST':
        def_id = q.definition_id
        q.delete()
        messages.success(request, 'Pregunta eliminada.')
        return redirect('quicktest:q_list', def_id=def_id)
    return render(request, 'quicktest/q_confirm_delete.html', {'question': q})
