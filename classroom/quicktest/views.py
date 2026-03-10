import csv
import io
import json
from functools import wraps
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from classroom.courses.models import Course, Module
from classroom.enrollments.models import Enrollment, LessonCompletion
from classroom.quicktest.forms import QuickTestDefinitionForm, QuickTestQuestionForm
from classroom.quicktest.models import QuickTest, QuickTestDefinition, QuickTestQuestion

PASSING_SCORE = 70


def _is_staff(user) -> bool:
    return bool(user.is_authenticated and (user.is_staff or user.is_superuser))


def _normalize_question_payload(item, idx):
    if not isinstance(item, dict):
        return None, f"Pregunta #{idx} inválida: debe ser un objeto."
    qtype = str(item.get("question_type", "mcq")).strip().lower()
    if qtype not in {
        QuickTestQuestion.QuestionType.MULTIPLE_CHOICE,
        QuickTestQuestion.QuestionType.TEXT,
        QuickTestQuestion.QuestionType.SIGNATURE,
    }:
        return None, f"Pregunta #{idx}: question_type inválido."

    text = str(item.get("text", "")).strip()
    if not text:
        return None, f"Pregunta #{idx}: text es obligatorio."

    payload = {
        "order": item.get("order"),
        "question_type": qtype,
        "text": text,
        "expected_text": str(item.get("expected_text", "")).strip(),
        "option_a": "",
        "option_b": "",
        "option_c": "",
        "option_d": "",
        "correct_option": "",
    }

    if qtype == QuickTestQuestion.QuestionType.MULTIPLE_CHOICE:
        required = {"option_a", "option_b", "option_c", "option_d", "correct_option"}
        missing = [f for f in required if not str(item.get(f, "")).strip()]
        if missing:
            return None, f"Pregunta #{idx} incompleta. Faltan: {', '.join(missing)}."
        correct = str(item.get("correct_option", "")).strip().upper()
        if correct not in {"A", "B", "C", "D"}:
            return None, f"Pregunta #{idx}: correct_option debe ser A, B, C o D."
        payload.update(
            {
                "option_a": str(item["option_a"]).strip(),
                "option_b": str(item["option_b"]).strip(),
                "option_c": str(item["option_c"]).strip(),
                "option_d": str(item["option_d"]).strip(),
                "correct_option": correct,
            }
        )

    if qtype == QuickTestQuestion.QuestionType.SIGNATURE:
        payload["expected_text"] = ""

    return payload, None


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not _is_staff(request.user):
            messages.error(request, "No autorizado.")
            return redirect("/")
        return view_func(request, *args, **kwargs)

    return _wrapped

@login_required
def quicktest_list(request):
    tests = (
        QuickTest.objects.filter(user=request.user)
        .select_related("module", "module__course")
        .order_by("-completed_at")
    )
    total_tests = tests.count()
    passed_tests = tests.filter(score__gte=PASSING_SCORE).count()
    avg_score = round(sum(float(t.score) for t in tests) / total_tests, 2) if total_tests else 0

    context = {
        "tests": tests,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "avg_score": avg_score,
        "passing_score": PASSING_SCORE,
        "is_staff_panel": _is_staff(request.user),
    }

    if context["is_staff_panel"]:
        definitions = (
            QuickTestDefinition.objects.select_related("module", "module__course")
            .annotate(questions_count=Count("questions"))
            .order_by("module__course__title", "module__order")
        )
        context["definitions"] = definitions

    return render(request, "quicktest/quicktest_list.html", context)

@login_required
def quicktest_detail(request, pk):
    test = get_object_or_404(
        QuickTest.objects.select_related("module", "module__course"),
        pk=pk,
        user=request.user,
    )
    return render(request, "quicktest/quicktest_detail.html", {"test": test, "passing_score": PASSING_SCORE})

@login_required
def quicktest_taking(request, module_id):
    module = get_object_or_404(Module, pk=module_id)

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

    qdef = QuickTestDefinition.objects.filter(module=module).first()
    if not qdef:
        messages.info(request, "Este módulo no tiene test. Puedes continuar.")
        return redirect("courses:next_module", module_id=module.id)

    total_lessons = module.lessons.count()
    if total_lessons:
        completed_lessons = LessonCompletion.objects.filter(
            enrollment=enrollment,
            lesson__module=module,
        ).count()
        if completed_lessons < total_lessons:
            messages.info(request, "Debes completar todas las lecciones del módulo antes de tomar el test.")
            return redirect("courses:module_detail", pk=module.id)

    class _QWrap:
        def __init__(self, qs):
            self._qs = qs

        def all(self):
            return self._qs

        def count(self):
            return self._qs.count()

    questions_qs = qdef.questions.all().order_by("order", "id")
    test_proxy = SimpleNamespace(questions=_QWrap(questions_qs))
    base_context = {
        "module": module,
        "test": test_proxy,
        "back_to_course_url": reverse("courses:my_course"),
        "retry_url": reverse("quicktest:quicktest_taking", kwargs={"module_id": module.id}),
        "next_url": reverse("courses:next_module", kwargs={"module_id": module.id}),
    }

    if request.method != "POST":
        return render(request, "courses/quicktest.html", base_context)

    def _norm_text(v):
        return " ".join((v or "").strip().lower().split())

    total = questions_qs.count()
    correct = 0
    for q in questions_qs:
        user_answer = (request.POST.get(f"question_{q.id}") or "").strip()

        if q.question_type == QuickTestQuestion.QuestionType.MULTIPLE_CHOICE:
            if user_answer == q.correct_option:
                correct += 1
        elif q.question_type == QuickTestQuestion.QuestionType.TEXT:
            expected = (q.expected_text or "").strip()
            if expected:
                if _norm_text(user_answer) == _norm_text(expected):
                    correct += 1
            elif user_answer:
                correct += 1
        elif q.question_type == QuickTestQuestion.QuestionType.SIGNATURE:
            user_full_name = (request.user.get_full_name() or "").strip()
            if user_full_name and _norm_text(user_answer) == _norm_text(user_full_name):
                correct += 1

    score = (correct / total) * 100 if total > 0 else 0
    passed = score >= PASSING_SCORE
    QuickTest.objects.update_or_create(
        user=request.user,
        module=module,
        defaults={"score": round(score, 2)},
    )

    context = {
        **base_context,
        "result": {
            "score": round(score, 2),
            "passed": passed,
            "correct": correct,
            "total": total,
            "passing_score": PASSING_SCORE,
        },
    }

    if passed:
        messages.success(request, "Test aprobado. Continuando...")
        return redirect("courses:next_module", module_id=module.id)

    messages.warning(request, f"No aprobaste (mínimo {PASSING_SCORE}). Intenta de nuevo.")
    context["next_url"] = None
    return render(request, "courses/quicktest.html", context)

@login_required
def quicktest_update(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    if request.method == "POST":
        try:
            score = float(request.POST.get("score", "0"))
        except (TypeError, ValueError):
            messages.error(request, "Puntaje inválido.")
            return redirect("quicktest:quicktest_update", pk=test.pk)
        test.score = max(0, min(100, round(score, 2)))
        test.save(update_fields=["score"])
        messages.success(request, "Resultado actualizado.")
        return redirect("quicktest:quicktest_detail", pk=test.pk)
    return render(request, "quicktest/quicktest_form.html", {"test": test})

@login_required
def quicktest_delete(request, pk):
    test = get_object_or_404(QuickTest, pk=pk, user=request.user)
    if request.method == "POST":
        test.delete()
        messages.success(request, "Resultado eliminado.")
        return redirect("quicktest:quicktest_list")
    return render(request, "quicktest/quicktest_confirm_delete.html", {"test": test})

@staff_required
def qdef_list(request):
    defs = (
        QuickTestDefinition.objects.select_related("module", "module__course")
        .annotate(questions_count=Count("questions"))
        .order_by("module__course__title", "module__order")
    )
    return render(request, "quicktest/qdef_list.html", {"definitions": defs})

@staff_required
def qdef_create(request):
    if request.method == "POST":
        form = QuickTestDefinitionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "QuickTest creado.")
            return redirect("quicktest:qdef_list")
    else:
        form = QuickTestDefinitionForm()
    return render(request, "quicktest/qdef_form.html", {"form": form})

@staff_required
def qdef_update(request, pk):
    qdef = get_object_or_404(QuickTestDefinition, pk=pk)
    if request.method == "POST":
        form = QuickTestDefinitionForm(request.POST, instance=qdef)
        if form.is_valid():
            form.save()
            messages.success(request, "QuickTest actualizado.")
            return redirect("quicktest:qdef_list")
    else:
        form = QuickTestDefinitionForm(instance=qdef)
    return render(request, "quicktest/qdef_form.html", {"form": form, "qdef": qdef})

@staff_required
def qdef_delete(request, pk):
    qdef = get_object_or_404(QuickTestDefinition, pk=pk)
    if request.method == "POST":
        qdef.delete()
        messages.success(request, "QuickTest eliminado.")
        return redirect("quicktest:qdef_list")
    return render(request, "quicktest/qdef_confirm_delete.html", {"qdef": qdef})

@staff_required
def q_list(request, def_id):
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    questions = qdef.questions.all().order_by("order", "id")
    return render(request, "quicktest/q_list.html", {"qdef": qdef, "questions": questions})

@staff_required
def q_create(request, def_id):
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    if request.method == "POST":
        form = QuickTestQuestionForm(request.POST, definition=qdef)
        if form.is_valid():
            question = form.save(commit=False)
            question.definition = qdef
            question.save()
            messages.success(request, "Pregunta creada.")
            return redirect("quicktest:q_list", def_id=qdef.id)
    else:
        next_order = qdef.questions.count()
        form = QuickTestQuestionForm(initial={"order": next_order}, definition=qdef)
    return render(request, "quicktest/q_form.html", {"form": form, "qdef": qdef})

@staff_required
def q_update(request, pk):
    question = get_object_or_404(QuickTestQuestion, pk=pk)
    if request.method == "POST":
        form = QuickTestQuestionForm(request.POST, instance=question, definition=question.definition)
        if form.is_valid():
            form.save()
            messages.success(request, "Pregunta actualizada.")
            return redirect("quicktest:q_list", def_id=question.definition_id)
    else:
        form = QuickTestQuestionForm(instance=question, definition=question.definition)
    return render(request, "quicktest/q_form.html", {"form": form, "qdef": question.definition, "question": question})

@staff_required
def q_delete(request, pk):
    question = get_object_or_404(QuickTestQuestion, pk=pk)
    if request.method == "POST":
        def_id = question.definition_id
        question.delete()
        messages.success(request, "Pregunta eliminada.")
        return redirect("quicktest:q_list", def_id=def_id)
    return render(request, "quicktest/q_confirm_delete.html", {"question": question})

@staff_required
def qdef_import_json(request, def_id):
    qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
    if request.method != "POST":
        return render(request, "quicktest/qdef_import_json.html", {"qdef": qdef})

    source_file = request.FILES.get("json_file")
    if not source_file:
        messages.error(request, "Debes seleccionar un archivo JSON.")
        return redirect("quicktest:qdef_import_json", def_id=qdef.id)

    try:
        payload = json.load(source_file)
    except json.JSONDecodeError:
        messages.error(request, "El archivo no es un JSON válido.")
        return redirect("quicktest:qdef_import_json", def_id=qdef.id)

    questions = payload.get("questions", []) if isinstance(payload, dict) else payload if isinstance(payload, list) else []
    if not isinstance(questions, list) or not questions:
        messages.error(request, "No se encontraron preguntas. Usa un array o {'questions': [...]} .")
        return redirect("quicktest:qdef_import_json", def_id=qdef.id)

    normalized = []
    for idx, item in enumerate(questions, start=1):
        row, error = _normalize_question_payload(item, idx)
        if error:
            messages.error(request, error)
            return redirect("quicktest:qdef_import_json", def_id=qdef.id)
        normalized.append(row)

    replace_existing = request.POST.get("replace_existing") == "on"
    with transaction.atomic():
        if replace_existing:
            qdef.questions.all().delete()
        base_order = 0 if replace_existing else (qdef.questions.count())
        rows = []
        for idx, row in enumerate(normalized):
            row_order = row.get("order")
            if row_order is None or str(row_order).strip() == "":
                row["order"] = base_order + idx
            else:
                row["order"] = int(row_order)
            rows.append(QuickTestQuestion(definition=qdef, **row))
        QuickTestQuestion.objects.bulk_create(rows)

    messages.success(request, f"Importación completada: {len(normalized)} pregunta(s).")
    return redirect("quicktest:q_list", def_id=qdef.id)


@staff_required
def qdef_import_course_json(request):
    if request.method != "POST":
        return render(request, "quicktest/qdef_import_course_json.html")

    source_file = request.FILES.get("json_file")
    if not source_file:
        messages.error(request, "Debes seleccionar un archivo JSON.")
        return redirect("quicktest:qdef_import_course_json")

    try:
        payload = json.load(source_file)
    except json.JSONDecodeError:
        messages.error(request, "El archivo no es un JSON válido.")
        return redirect("quicktest:qdef_import_course_json")

    if not isinstance(payload, dict):
        messages.error(request, "El JSON debe ser un objeto.")
        return redirect("quicktest:qdef_import_course_json")

    course_ref = payload.get("course_id") or payload.get("course")
    modules_payload = payload.get("modules", [])
    if not course_ref or not isinstance(modules_payload, list) or not modules_payload:
        messages.error(request, "Debes incluir course/course_id y modules (lista).")
        return redirect("quicktest:qdef_import_course_json")

    if str(course_ref).isdigit():
        course = Course.objects.filter(pk=int(course_ref)).first()
    else:
        course = Course.objects.filter(title__iexact=str(course_ref).strip()).first()

    if not course:
        messages.error(request, "Curso no encontrado.")
        return redirect("quicktest:qdef_import_course_json")

    replace_existing = request.POST.get("replace_existing") == "on" or bool(payload.get("replace_existing"))

    created_defs = 0
    imported_questions = 0

    with transaction.atomic():
        for m_idx, m_item in enumerate(modules_payload, start=1):
            if not isinstance(m_item, dict):
                messages.error(request, f"Módulo #{m_idx} inválido.")
                return redirect("quicktest:qdef_import_course_json")

            module_ref = m_item.get("module_id") or m_item.get("module")
            questions = m_item.get("questions", [])
            if not module_ref:
                messages.error(request, f"Módulo #{m_idx}: falta module/module_id.")
                return redirect("quicktest:qdef_import_course_json")
            if not isinstance(questions, list) or not questions:
                messages.error(request, f"Módulo #{m_idx}: no tiene preguntas.")
                return redirect("quicktest:qdef_import_course_json")

            if str(module_ref).isdigit():
                module = Module.objects.filter(pk=int(module_ref), course=course).first()
            else:
                module = Module.objects.filter(course=course, title__iexact=str(module_ref).strip()).first()

            if not module:
                messages.error(request, f"Módulo '{module_ref}' no encontrado en el curso '{course.title}'.")
                return redirect("quicktest:qdef_import_course_json")

            default_title = f"QuickTest - {module.title}"
            qdef, was_created = QuickTestDefinition.objects.get_or_create(
                module=module,
                defaults={"title": m_item.get("title") or default_title},
            )
            if not was_created and m_item.get("title"):
                qdef.title = str(m_item["title"]).strip() or qdef.title
                qdef.save(update_fields=["title"])
            if was_created:
                created_defs += 1

            normalized = []
            for q_idx, q_item in enumerate(questions, start=1):
                row, error = _normalize_question_payload(q_item, q_idx)
                if error:
                    messages.error(request, f"Módulo '{module.title}': {error}")
                    return redirect("quicktest:qdef_import_course_json")
                normalized.append(row)

            if replace_existing:
                qdef.questions.all().delete()
            base_order = 0 if replace_existing else qdef.questions.count()
            rows = []
            for idx, row in enumerate(normalized):
                row_order = row.get("order")
                if row_order is None or str(row_order).strip() == "":
                    row["order"] = base_order + idx
                else:
                    row["order"] = int(row_order)
                rows.append(QuickTestQuestion(definition=qdef, **row))
            QuickTestQuestion.objects.bulk_create(rows)
            imported_questions += len(normalized)

    messages.success(
        request,
        f"Importación por curso completada. Curso: {course.title}. Definiciones nuevas: {created_defs}. Preguntas importadas: {imported_questions}."
    )
    return redirect("quicktest:qdef_list")

@staff_required
def qdef_export_csv(request, def_id):
    try:
        qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
        questions = qdef.questions.all().order_by("order", "id")

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="quicktest_{qdef.id}_questions.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(
            [
                "question_type",
                "order",
                "text",
                "expected_text",
                "option_a",
                "option_b",
                "option_c",
                "option_d",
                "correct_option",
            ]
        )
        for q in questions:
            writer.writerow(
                [
                    q.question_type,
                    q.order,
                    q.text,
                    q.expected_text,
                    q.option_a,
                    q.option_b,
                    q.option_c,
                    q.option_d,
                    q.correct_option,
                ]
            )
        messages.success(request, f"Exportación CSV completada para '{qdef.title}'.")
        return response
    except Exception as exc:
        messages.error(request, f"Error exportando CSV: {exc}")
        return redirect("quicktest:qdef_list")

@staff_required
def qdef_export_pdf(request, def_id):
    try:
        qdef = get_object_or_404(QuickTestDefinition, pk=def_id)
        questions = qdef.questions.all().order_by("order", "id")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"QuickTest: {qdef.title}", styles["Heading2"]),
            Paragraph(f"Curso: {qdef.module.course.title}", styles["Normal"]),
            Paragraph(f"Módulo: {qdef.module.title}", styles["Normal"]),
            Spacer(1, 12),
        ]

        for idx, q in enumerate(questions, start=1):
            story.append(Paragraph(f"{idx}. [Orden {q.order}] {q.text}", styles["Normal"]))
            story.append(Paragraph(f"Tipo: {q.get_question_type_display()}", styles["Normal"]))
            if q.question_type == QuickTestQuestion.QuestionType.MULTIPLE_CHOICE:
                story.append(Paragraph(f"A) {q.option_a}", styles["Normal"]))
                story.append(Paragraph(f"B) {q.option_b}", styles["Normal"]))
                story.append(Paragraph(f"C) {q.option_c}", styles["Normal"]))
                story.append(Paragraph(f"D) {q.option_d}", styles["Normal"]))
                story.append(Paragraph(f"Correcta: {q.correct_option}", styles["Normal"]))
            elif q.question_type == QuickTestQuestion.QuestionType.TEXT:
                story.append(Paragraph(f"Respuesta esperada: {q.expected_text or '(cualquier respuesta no vacia)'}", styles["Normal"]))
            else:
                story.append(Paragraph("Debe firmar escribiendo su nombre completo.", styles["Normal"]))
            story.append(Spacer(1, 10))

        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="quicktest_{qdef.id}_questions.pdf"'
        messages.success(request, f"Exportación PDF completada para '{qdef.title}'.")
        return response
    except Exception as exc:
        messages.error(request, f"Error exportando PDF: {exc}")
        return redirect("quicktest:qdef_list")
