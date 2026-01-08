from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = (
        "Seed DEMO quicktests: create 5 multiple-choice questions per module "
        "for the course 'DEMO – Prevención del Uso de Alcohol, Tabaco y Otras Drogas' "
        "inside classroom.quicktest. Idempotent: deletes and recreates questions per module."
    )

    COURSE_TITLE = "DEMO – Prevención del Uso de Alcohol, Tabaco y Otras Drogas"

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Print actions without writing changes')

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        try:
            from classroom.courses.models import Course, Module
            from classroom.quicktest.models import QuickTestDefinition, QuickTestQuestion
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Import error: {e}"))
            return

        course = Course.objects.filter(title=self.COURSE_TITLE).first()
        if not course:
            self.stderr.write(self.style.ERROR(f"Course not found by exact title: {self.COURSE_TITLE}"))
            return

        modules = list(Module.objects.filter(course=course).order_by('order'))
        if not modules:
            self.stderr.write(self.style.ERROR("No modules found for DEMO course."))
            return

        # Distinct demo question sets per module index (1-based)
        questions_by_module_index = {
            1: [
                {
                    'text': '¿Cuál es un factor de protección frente al consumo?',
                    'option_a': 'Vínculo familiar fuerte y comunicación abierta',
                    'option_b': 'Falta de supervisión de adultos',
                    'option_c': 'Consumo temprano en la adolescencia',
                    'option_d': 'Participación en pandillas',
                    'correct_option': 'A',
                },
                {
                    'text': '¿Qué ejemplo refleja un factor de riesgo en adolescentes?',
                    'option_a': 'Red de amistades sanas',
                    'option_b': 'Presión de pares para “probar” sustancias',
                    'option_c': 'Participación en deportes',
                    'option_d': 'Comunicación efectiva en casa',
                    'correct_option': 'B',
                },
                {
                    'text': '¿Qué acción fortalece factores de protección?',
                    'option_a': 'Normalizar el consumo en reuniones',
                    'option_b': 'Evitar hablar del tema en familia',
                    'option_c': 'Fomentar actividades extracurriculares y apoyo escolar',
                    'option_d': 'Permitir el consumo “con moderación”',
                    'correct_option': 'C',
                },
                {
                    'text': '¿Cuál es un factor de protección a nivel escolar?',
                    'option_a': 'Ausentismo frecuente',
                    'option_b': 'Bajo rendimiento no atendido',
                    'option_c': 'Programas de prevención y tutorías',
                    'option_d': 'Ambiente de violencia',
                    'correct_option': 'C',
                },
                {
                    'text': '¿Qué describe mejor un factor de riesgo familiar?',
                    'option_a': 'Normas claras y límites consistentes',
                    'option_b': 'Escasa supervisión y límites difusos',
                    'option_c': 'Tiempo de calidad en familia',
                    'option_d': 'Refuerzo de logros',
                    'correct_option': 'B',
                },
            ],
            2: [
                {
                    'text': 'La etapa primaria/experimental se caracteriza por…',
                    'option_a': 'Consumo diario y dependencia',
                    'option_b': 'Uso frecuente con consecuencias negativas',
                    'option_c': 'Primeros intentos por curiosidad, sin patrón establecido',
                    'option_d': 'Rehabilitación y tratamiento',
                    'correct_option': 'C',
                },
                {
                    'text': 'La etapa secundaria/abuso suele implicar…',
                    'option_a': 'Uso repetido que afecta escuela y familia',
                    'option_b': 'Ningún impacto en el rendimiento',
                    'option_c': 'Solo consumo experimental',
                    'option_d': 'Tratamiento especializado',
                    'correct_option': 'A',
                },
                {
                    'text': 'La etapa terciaria/consumo diario indica…',
                    'option_a': 'Curiosidad ocasional',
                    'option_b': 'Dependencia y necesidad de intervención',
                    'option_c': 'Abandono total del consumo',
                    'option_d': 'Sin consecuencias en salud',
                    'correct_option': 'B',
                },
                {
                    'text': '¿Qué señal encaja con consumo problemático (abuso)?',
                    'option_a': 'Participación estable en clases',
                    'option_b': 'Conflictos frecuentes y baja motivación',
                    'option_c': 'Hábitos saludables constantes',
                    'option_d': 'Relaciones familiares positivas',
                    'correct_option': 'B',
                },
                {
                    'text': 'En la etapa experimental, es común…',
                    'option_a': 'Probar por presión de pares',
                    'option_b': 'Recaídas después del tratamiento',
                    'option_c': 'Síntomas de abstinencia severos',
                    'option_d': 'Consumo crónico',
                    'correct_option': 'A',
                },
            ],
            3: [
                {
                    'text': 'Un impacto frecuente del consumo en la escuela es…',
                    'option_a': 'Mejor concentración',
                    'option_b': 'Aumento del rendimiento académico',
                    'option_c': 'Ausencias, conflictos y bajo rendimiento',
                    'option_d': 'Mayor integración en actividades',
                    'correct_option': 'C',
                },
                {
                    'text': 'Una medida de prevención comunitaria efectiva es…',
                    'option_a': 'Tolerancia al consumo en eventos',
                    'option_b': 'Campañas educativas y apoyo interinstitucional',
                    'option_c': 'Evitar hablar del tema',
                    'option_d': 'Normalizar “probar una vez”',
                    'correct_option': 'B',
                },
                {
                    'text': 'Una decisión saludable frente a la presión de pares es…',
                    'option_a': 'Ceder “por una vez”',
                    'option_b': 'Buscar apoyo y decir no',
                    'option_c': 'Alejarse de actividades positivas',
                    'option_d': 'Ocultar la situación',
                    'correct_option': 'B',
                },
                {
                    'text': '¿Qué acción familiar ayuda a la prevención?',
                    'option_a': 'Evitar conversaciones sobre riesgos',
                    'option_b': 'Comunicación abierta y límites claros',
                    'option_c': 'Ignorar señales de alerta',
                    'option_d': 'Permitir consumo “bajo control”',
                    'correct_option': 'B',
                },
                {
                    'text': '¿Qué enfoque fortalece decisiones saludables?',
                    'option_a': 'Informarse, planificar respuestas y buscar apoyo',
                    'option_b': 'Actuar sin pensar',
                    'option_c': 'Aislarse del entorno',
                    'option_d': 'Aceptar cualquier presión',
                    'correct_option': 'A',
                },
            ],
        }

        total_defs = 0
        total_questions = 0
        for idx, module in enumerate(modules, start=1):
            title = f"QuickTest DEMO - Módulo {idx}"
            qdef, created = QuickTestDefinition.objects.get_or_create(
                module=module,
                defaults={'title': title}
            )
            # If it exists, ensure title is set (optional update)
            if not created and qdef.title != title:
                if not dry_run:
                    qdef.title = title
                    qdef.save(update_fields=['title'])

            # Idempotent: delete and recreate 5 questions for this definition
            existing_count = qdef.questions.count()
            if not dry_run:
                qdef.questions.all().delete()
            created_ids = []
            module_questions = questions_by_module_index.get(idx) or questions_by_module_index.get(3)
            for q in module_questions:
                if not dry_run:
                    qq = QuickTestQuestion.objects.create(definition=qdef, **q)
                    created_ids.append(qq.id)
            total_defs += 1
            total_questions += len(module_questions)
            self.stdout.write(self.style.SUCCESS(
                f"Module {module.id} | QDef {qdef.id} | replaced {existing_count} -> created {len(module_questions)}"
            ))
            if created_ids:
                self.stdout.write("  Question IDs: " + ", ".join(map(str, created_ids)))

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete. Definitions: {total_defs}, Questions: {total_questions}"
        ))
