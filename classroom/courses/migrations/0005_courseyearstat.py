from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_course_about_blurb_course_manual_certified_add_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseYearStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField()),
                ('manual_certified_add', models.PositiveIntegerField(default=0)),
                ('note', models.CharField(blank=True, max_length=255)),
                (
                    'course',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='year_stats', to='courses.course'),
                ),
            ],
            options={
                'ordering': ['-year'],
                'unique_together': {('course', 'year')},
            },
        ),
    ]
