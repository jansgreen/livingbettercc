from django.core.management.base import BaseCommand
from django.db import transaction

from classroom.courses.models import Course, Module, Lesson
from classroom.quicktest.models import QuickTestDefinition, QuickTestQuestion


class Command(BaseCommand):
    help = "Seed a demo course with modules, lessons, tests, and questions. Idempotent by title."

    @transaction.atomic
    def handle(self, *args, **options):
        title = "DEMO – Prevención del Uso de Alcohol, Tabaco y Otras Drogas"
        description = (
            "Este es un curso DEMO diseñado para visualizar, probar y presentar el funcionamiento "
            "del Classroom de LBCC. No es un programa académico real; su propósito es mostrar el "
            "flujo de módulos, lecciones, evaluaciones y progreso basado en valores educativos y de prevención."
        )

        course, created = Course.objects.get_or_create(
            title=title,
            defaults={
                "description": description,
                "published": True,
                "price": 0,
            },
        )

        if not created:
            # Ensure demo attributes are correct and reset children for idempotency
            course.description = description
            course.published = True
            course.price = 0
            course.save(update_fields=["description", "published", "price"])

            # Remove existing related content to re-seed cleanly
            # Cascade deletes tests, questions, lessons via FKs/OneToOne
            course.modules.all().delete()

        # Seed modules, lessons, quicktest definitions, and questions
        modules_spec = [
            {
                "order": 1,
                "title": "Fundamentos de Prevención",
                "description": "Conceptos básicos sobre drogas y prevención.",
                "lessons": [
                    (1, "¿Qué son las drogas?", "Definición simple y ejemplos cotidianos. Enfatiza que incluyen sustancias legales e ilegales."),
                    (2, "Tipos de drogas más comunes", "Alcohol, tabaco, marihuana y fármacos mal utilizados; riesgos generales."),
                    (3, "Riesgos del consumo temprano", "Impacto en el cerebro en desarrollo, decisiones y relaciones."),
                ],
                "questions": [
                    {
                        "text": "¿Qué describe mejor el término 'drogas'?",
                        "A": "Solo sustancias ilegales",
                        "B": "Sustancias que alteran el cuerpo o la mente",
                        "C": "Solo medicamentos recetados",
                        "D": "Alimentos y bebidas",
                        "correct": "B",
                    },
                    {
                        "text": "¿Cuál de estas es una droga legal para adultos, pero riesgosa?",
                        "A": "Agua",
                        "B": "Alcohol",
                        "C": "Vitaminas",
                        "D": "Frutas",
                        "correct": "B",
                    },
                    {
                        "text": "Consumir a edad temprana aumenta el riesgo de…",
                        "A": "Tener mayor control",
                        "B": "Mejor memoria",
                        "C": "Problemas de salud y decisiones riesgosas",
                        "D": "Más horas de estudio",
                        "correct": "C",
                    },
                ],
            },
            {
                "order": 2,
                "title": "Impacto Social y Escolar",
                "description": "Efectos en la escuela, familia y comunidad.",
                "lessons": [
                    (1, "Consecuencias en la escuela", "Ausencias, bajo rendimiento y conflictos con normas escolares."),
                    (2, "Impacto familiar", "Tensiones en la comunicación, confianza y convivencia."),
                    (3, "Prevención comunitaria", "El papel de la escuela, familia y comunidad en la prevención."),
                ],
                "questions": [
                    {
                        "text": "Un posible efecto del consumo en la escuela es…",
                        "A": "Mejor concentración",
                        "B": "Bajo rendimiento y faltas",
                        "C": "Más participación",
                        "D": "Premios académicos",
                        "correct": "B",
                    },
                    {
                        "text": "La familia puede ayudar a prevenir mediante…",
                        "A": "Silencio y evitar el tema",
                        "B": "Comunicación clara y apoyo",
                        "C": "Castigos sin explicación",
                        "D": "Ignorar señales",
                        "correct": "B",
                    },
                    {
                        "text": "La comunidad apoya la prevención cuando…",
                        "A": "Promueve espacios seguros y educación",
                        "B": "Evita actividades saludables",
                        "C": "Fomenta la desinformación",
                        "D": "Aísla a las familias",
                        "correct": "A",
                    },
                ],
            },
            {
                "order": 3,
                "title": "Decisiones y Protección",
                "description": "Factores de riesgo/protección y toma de decisiones.",
                "lessons": [
                    (1, "Factores de riesgo", "Presión de pares, baja supervisión y manejo emocional limitado."),
                    (2, "Factores de protección", "Apoyo familiar, metas claras y actividades positivas."),
                    (3, "Tomando buenas decisiones", "Estrategias para decir no y buscar ayuda."),
                ],
                "questions": [
                    {
                        "text": "¿Cuál es un factor de riesgo?",
                        "A": "Metas claras",
                        "B": "Apoyo familiar",
                        "C": "Presión de pares para consumir",
                        "D": "Actividades deportivas",
                        "correct": "C",
                    },
                    {
                        "text": "¿Qué ayuda como factor de protección?",
                        "A": "Aislarse",
                        "B": "Tener redes de apoyo",
                        "C": "Desinformarse",
                        "D": "Normalizar el consumo",
                        "correct": "B",
                    },
                    {
                        "text": "Una estrategia para decidir bien es…",
                        "A": "Ceder a la presión",
                        "B": "Evitar pedir ayuda",
                        "C": "Decir no y acudir a un adulto de confianza",
                        "D": "Ignorar las consecuencias",
                        "correct": "C",
                    },
                ],
            },
        ]

        self.stdout.write(self.style.SUCCESS(f"Course: {course.id} - {course.title} (published={course.published}, price={course.price})"))

        created_modules = []
        created_lessons = []
        created_defs = []
        created_questions = []

        for mod in modules_spec:
            module = Module.objects.create(
                course=course,
                title=mod["title"],
                description=mod["description"],
                order=mod["order"],
            )
            created_modules.append(module)
            self.stdout.write(f"  Module[{module.order}]: id={module.id} - {module.title}")

            # Lessons
            for order, lt, lc in mod["lessons"]:
                lesson = Lesson.objects.create(
                    module=module,
                    title=lt,
                    content=lc,
                    order=order,
                )
                created_lessons.append(lesson)
                self.stdout.write(f"    Lesson[{lesson.order}]: id={lesson.id} - {lesson.title}")

            # Quicktest Definition
            qdef = QuickTestDefinition.objects.create(module=module, title=f"Test – {module.title}")
            created_defs.append(qdef)
            self.stdout.write(f"    QuickTestDefinition: id={qdef.id} - {qdef.title}")

            # Questions (3 per module)
            for q in mod["questions"]:
                question = QuickTestQuestion.objects.create(
                    definition=qdef,
                    text=q["text"],
                    option_a=q["A"],
                    option_b=q["B"],
                    option_c=q["C"],
                    option_d=q["D"],
                    correct_option=q["correct"],
                )
                created_questions.append(question)
                self.stdout.write(
                    f"      Question: id={question.id} (correct={question.correct_option})"
                )

        # Sanity checks per module
        self.stdout.write("")
        for m in created_modules:
            has_test = hasattr(m, "quicktest_definition") and m.quicktest_definition is not None
            q_count = m.quicktest_definition.questions.count() if has_test else 0
            ok = has_test and q_count > 0
            status = self.style.SUCCESS("OK") if ok else self.style.ERROR("FAIL")
            self.stdout.write(f"Check module id={m.id}: test={has_test}, questions={q_count} -> {status}")

        self.stdout.write("")
        self.stdout.write(self.style.WARNING("Access via URL name:"))
        self.stdout.write(self.style.WARNING(f"  courses:course_detail (pk={course.id})"))

        # Final summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seeding completed."))
        self.stdout.write(
            f"Totals -> Course:1, Modules:{len(created_modules)}, Lessons:{len(created_lessons)}, QuickTestDefs:{len(created_defs)}, Questions:{len(created_questions)}"
        )
