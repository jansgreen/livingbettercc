from django.db import migrations, models


def seed_scholarship_assignment(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    SystemFormAssignment = apps.get_model('formbuilder', 'SystemFormAssignment')

    assignment, _ = SystemFormAssignment.objects.get_or_create(
        key='scholarship_student_info'
    )
    aliases = {
        'estudiantes_becados',
        'estudiante_becado',
        'estudiantes becados',
        'estudiante becado',
    }
    groups = []
    for group in Group.objects.all():
        normalized = (group.name or '').strip().lower().replace('_', ' ')
        if normalized in aliases:
            groups.append(group)
    if groups:
        assignment.assigned_groups.add(*groups)


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('formbuilder', '0017_formdefinition_assigned_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemFormAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(choices=[('scholarship_student_info', 'Datos del estudiante becado')], max_length=100, unique=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_groups', models.ManyToManyField(blank=True, help_text='Grupos para los que se activa este formulario del sistema.', related_name='assigned_system_forms', to='auth.group')),
            ],
            options={
                'ordering': ['key'],
            },
        ),
        migrations.RunPython(seed_scholarship_assignment, migrations.RunPython.noop),
    ]
