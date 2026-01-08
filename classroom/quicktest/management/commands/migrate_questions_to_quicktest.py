from django.core.management.base import BaseCommand
from django.db import transaction

from classroom.courses.models import Module
from classroom.quicktest.models import QuickTestDefinition, QuickTestQuestion


class Command(BaseCommand):
    help = "Copy existing courses Test/Question into quicktest definitions/questions. Idempotent per module."

    @transaction.atomic
    def handle(self, *args, **options):
        modules = Module.objects.all()
        created_defs = 0
        created_qs = 0
        updated_defs = 0
        skipped = 0

        for module in modules:
            test = getattr(module, 'test', None)
            if not test:
                skipped += 1
                continue

            qdef, created = QuickTestDefinition.objects.get_or_create(
                module=module,
                defaults={"title": getattr(test, 'title', f"Test – {module.title}")}
            )
            if created:
                created_defs += 1
            else:
                # Keep title in sync if changed
                if qdef.title != getattr(test, 'title', qdef.title):
                    qdef.title = getattr(test, 'title', qdef.title)
                    qdef.save(update_fields=["title"])
                    updated_defs += 1

            # Build a set of existing question signatures to avoid dupes
            existing = set(
                (q.text, q.option_a, q.option_b, q.option_c, q.option_d, q.correct_option)
                for q in qdef.questions.all()
            )

            for cq in test.questions.all():
                sig = (cq.text, cq.option_a, cq.option_b, cq.option_c, cq.option_d, cq.correct_option)
                if sig in existing:
                    continue
                QuickTestQuestion.objects.create(
                    definition=qdef,
                    text=cq.text,
                    option_a=cq.option_a,
                    option_b=cq.option_b,
                    option_c=cq.option_c,
                    option_d=cq.option_d,
                    correct_option=cq.correct_option,
                )
                created_qs += 1

            self.stdout.write(
                f"Module id={module.id} '{module.title}': def_id={qdef.id} (created={created}) | total_qs={qdef.questions.count()}"
            )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Done. defs_created={created_defs}, defs_updated={updated_defs}, qs_created={created_qs}, modules_without_test={skipped}"
        ))
