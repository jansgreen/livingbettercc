from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('formbuilder', '0015_standardize_text_fields_to_selects'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationalCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('number', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('distrito', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='ImpactsBefore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_disappointment', models.IntegerField()),
                ('family_conflict', models.IntegerField()),
                ('dysfunctional_homes', models.IntegerField()),
                ('health_problems', models.IntegerField()),
                ('mental_health_problems', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ImpactsPositive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school_level', models.IntegerField()),
                ('family_level', models.IntegerField()),
                ('social', models.IntegerField()),
                ('improvement_in_school_disappointment', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='attached_files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/%Y/%m/%d/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='TrimestralReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('tittle', models.TextField(blank=True, null=True)),
                ('distrite', models.CharField(blank=True, help_text='Distrito del facilitador', max_length=100, null=True)),
                ('goals', models.TextField(blank=True, null=True)),
                ('methodology', models.TextField(blank=True, null=True)),
                ('experience', models.TextField(blank=True, null=True)),
                ('observations', models.TextField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('male', 'Masculino'), ('female', 'Femenino')], max_length=50, null=True)),
                ('trimestre', models.CharField(max_length=20)),
                ('year', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('educational_center', models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='formbuilder.educationalcenter')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to='auth.user')),
            ],
        ),
        migrations.AddField(
            model_name='trimestralreport',
            name='attached_files',
            field=models.ManyToManyField(blank=True, to='formbuilder.attached_files'),
        ),
        migrations.AlterField(
            model_name='impactsbefore',
            name='school_disappointment',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactsbefore',
            name='family_conflict',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactsbefore',
            name='dysfunctional_homes',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactsbefore',
            name='health_problems',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactsbefore',
            name='mental_health_problems',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactspositive',
            name='school_level',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactspositive',
            name='family_level',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactspositive',
            name='social',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='impactspositive',
            name='improvement_in_school_disappointment',
            field=models.IntegerField(),
        ),
    ]
