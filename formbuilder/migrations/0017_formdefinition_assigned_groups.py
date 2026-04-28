from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('formbuilder', '0016_remove_integer_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='formdefinition',
            name='assigned_groups',
            field=models.ManyToManyField(
                blank=True,
                help_text='Grupos que pueden ver y completar este formulario.',
                related_name='assigned_form_definitions',
                to='auth.group',
            ),
        ),
    ]
