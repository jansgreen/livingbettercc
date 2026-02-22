from django.db import migrations


FORM_NAME = (
    'Evidencias trimestrales sobre la implementación del proyecto '
    '"La educacion temprana sobre el Uso del Tabaco, Alcohol y otras Drogas, '
    'previene que nuestros jóvenes no se enfermen Bio-psicosocial".'
)


STANDARD_CHOICES = {
    'metodologia': [
        'Taller presencial',
        'Charlas educativas',
        'Sesiones grupales',
        'Visitas a centros educativos',
        'Material impreso / guías',
        'Actividades lúdicas',
        'Mentorías / acompañamiento',
        'Charlas con padres / tutores',
        'Virtual / online',
    ],
    'puntos_destacados': [
        'Alta participación de estudiantes',
        'Buena receptividad del centro educativo',
        'Participación de docentes',
        'Participación de padres / tutores',
        'Mejoras en el conocimiento del tema',
        'Buen comportamiento del grupo',
        'Dinámicas efectivas',
        'Interés continuo después del taller',
    ],
    'principales_incidencias': [
        'Baja asistencia',
        'Falta de apoyo del centro',
        'Problemas logísticos',
        'Falta de materiales',
        'Baja participación',
        'Resistencia al tema',
        'Conflictos entre estudiantes',
        'Retrasos en el cronograma',
        'Ninguna incidencia',
    ],
}


def forwards(apps, schema_editor):
    FormDefinition = apps.get_model('formbuilder', 'FormDefinition')
    FormField = apps.get_model('formbuilder', 'FormField')

    try:
        form_def = FormDefinition.objects.get(name=FORM_NAME)
    except FormDefinition.DoesNotExist:
        return

    for name, choices in STANDARD_CHOICES.items():
        choices_str = ','.join(choices)
        FormField.objects.filter(form=form_def, name=name).update(
            field_type='select',
            choices=choices_str,
        )


def backwards(apps, schema_editor):
    FormDefinition = apps.get_model('formbuilder', 'FormDefinition')
    FormField = apps.get_model('formbuilder', 'FormField')

    try:
        form_def = FormDefinition.objects.get(name=FORM_NAME)
    except FormDefinition.DoesNotExist:
        return

    FormField.objects.filter(form=form_def, name__in=STANDARD_CHOICES.keys()).update(
        field_type='text',
        choices=None,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('formbuilder', '0014_backfill_completedform_form'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
