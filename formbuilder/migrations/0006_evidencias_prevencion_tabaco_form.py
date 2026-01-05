from __future__ import annotations

from django.db import migrations


FORM_NAME = (
    'Evidencias trimestrales sobre la implementación del proyecto '
    '"La educacion temprana sobre el Uso del Tabaco, Alcohol y otras Drogas, '
    'previene que nuestros jóvenes no se enfermen Bio-psicosocial".'
)

FORM_DESCRIPTION = (
    'Medir el impacto de la implementación de los talleres sobre prevención de '
    'Tabaco, Alcohol y otras Drogas, en adolescentes, de centros educativos de '
    'la regional de educacion 07.'
)


FIELDS = [
    # Table 1 (header fields)
    {
        'label': 'Centro Educativo',
        'name': 'centro_educativo',
        'field_type': 'char',
        'required': True,
        'choices': None,
    },
    {
        'label': 'Responsables',
        'name': 'responsables',
        'field_type': 'char',
        'required': True,
        'choices': None,
    },
    {
        'label': 'Fechas',
        'name': 'fechas',
        'field_type': 'char',
        'required': True,
        'choices': None,
    },
    {
        'label': 'Temas impartidos',
        'name': 'temas_impartidos',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },

    # Body
    {
        'label': 'Objetivo/Razón/Motivo',
        'name': 'objetivo_razon_motivo',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Como realizo la multiplicación (metodología)',
        'name': 'metodologia',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Puntos destacados del proceso (ver la experiencia)',
        'name': 'puntos_destacados',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Principales incidencias (Observaciones)',
        'name': 'principales_incidencias',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },

    # Personas impactadas
    {
        'label': 'Personas impactas, Femenino',
        'name': 'personas_impactadas_femenino',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Personas impactas, Masculino',
        'name': 'personas_impactadas_masculino',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Personas impactas, Edades',
        'name': 'personas_impactadas_edades',
        'field_type': 'char',
        'required': False,
        'choices': None,
    },

    # Impacto antes (por consecuencia del uso y abuso)
    {
        'label': 'Impacto antes: Decepción Escolar',
        'name': 'impacto_antes_decepcion_escolar',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Impacto antes: Conflicto familiar',
        'name': 'impacto_antes_conflicto_familiar',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Impacto antes: Hogares disfuncionales',
        'name': 'impacto_antes_hogares_disfuncionales',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Impacto antes: Problemas de salud (inducida)',
        'name': 'impacto_antes_problemas_salud',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Impacto antes: Problemas mentales (inducida)',
        'name': 'impacto_antes_problemas_mentales',
        'field_type': 'integer',
        'required': False,
        'choices': None,
    },

    # Impacto positivo
    {
        'label': 'Impacto positivo a raíz de la implementación del proyecto: A nivel escolar',
        'name': 'impacto_positivo_nivel_escolar',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Impacto positivo a raíz de la implementación del proyecto: A nivel familiar',
        'name': 'impacto_positivo_nivel_familiar',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Impacto positivo a raíz de la implementación del proyecto: Social',
        'name': 'impacto_positivo_social',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
    {
        'label': 'Mejora en la decepción escolar',
        'name': 'mejora_decepcion_escolar',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },

    # Anexos
    {
        'label': 'Anexos (fotos, videos, listados y otros)',
        'name': 'anexos',
        'field_type': 'text',
        'required': False,
        'choices': None,
    },
]


def forwards(apps, schema_editor):
    FormDefinition = apps.get_model('formbuilder', 'FormDefinition')
    FormField = apps.get_model('formbuilder', 'FormField')

    form_def, _created = FormDefinition.objects.get_or_create(
        name=FORM_NAME,
        defaults={'description': FORM_DESCRIPTION},
    )

    # Keep description synced if it changed
    if (form_def.description or '') != FORM_DESCRIPTION:
        form_def.description = FORM_DESCRIPTION
        form_def.save(update_fields=['description'])

    existing = set(
        FormField.objects.filter(form=form_def).values_list('name', flat=True)
    )

    order = 1
    for f in FIELDS:
        if f['name'] in existing:
            continue
        FormField.objects.create(
            form=form_def,
            label=f['label'],
            name=f['name'],
            field_type=f['field_type'],
            required=f['required'],
            choices=f['choices'],
            order=order,
        )
        order += 1


def backwards(apps, schema_editor):
    FormDefinition = apps.get_model('formbuilder', 'FormDefinition')
    FormField = apps.get_model('formbuilder', 'FormField')

    try:
        form_def = FormDefinition.objects.get(name=FORM_NAME)
    except FormDefinition.DoesNotExist:
        return

    FormField.objects.filter(form=form_def).delete()
    form_def.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('formbuilder', '0005_completedform_address_completedform_distrito'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
