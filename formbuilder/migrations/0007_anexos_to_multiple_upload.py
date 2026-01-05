from __future__ import annotations

from django.db import migrations


FORM_NAME_PREFIX = 'Evidencias trimestrales sobre la implementación del proyecto'


def forwards(apps, schema_editor):
    FormDefinition = apps.get_model('formbuilder', 'FormDefinition')
    FormField = apps.get_model('formbuilder', 'FormField')

    # Update all 'anexos' fields to the new multi-upload type.
    # (Keeps this change global as requested: "todos los formularios").
    qs = FormField.objects.filter(name='anexos')
    for f in qs:
        if f.field_type != 'files':
            f.field_type = 'files'
        # For attachments, it's safer to not require.
        if f.required:
            f.required = False
        f.save(update_fields=['field_type', 'required'])


def backwards(apps, schema_editor):
    FormField = apps.get_model('formbuilder', 'FormField')

    # Revert 'anexos' back to text area.
    qs = FormField.objects.filter(name='anexos')
    for f in qs:
        f.field_type = 'text'
        f.save(update_fields=['field_type'])


class Migration(migrations.Migration):
    dependencies = [
        ('formbuilder', '0006_evidencias_prevencion_tabaco_form'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
