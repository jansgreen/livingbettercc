# Create your models here.
# courses/models.py
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Program(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = CKEditor5Field('course description')
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    manual_certified_add = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    @property
    def certified_auto_count(self) -> int:
        annotated = getattr(self, 'auto_certified_count', None)
        if annotated is not None:
            return int(annotated)
        return int(self.certificates.count())

    @property
    def certified_total(self) -> int:
        annotated = getattr(self, 'total_certified_count', None)
        if annotated is not None:
            return int(annotated)
        manual_year = self.year_stats.aggregate(total=Coalesce(Sum('manual_certified_add'), 0)).get('total') or 0
        return int(self.certified_auto_count) + int(self.manual_certified_add) + int(manual_year)

class CourseYearStat(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='year_stats')
    year = models.PositiveIntegerField()
    manual_certified_add = models.PositiveIntegerField(default=0)
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-year']
        unique_together = ('course', 'year')

    def __str__(self):
        return f"{self.course.title} - {self.year} (+{self.manual_certified_add})"

class ProgramYearStat(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='year_stats')
    year = models.PositiveIntegerField()
    in_person_certified = models.PositiveIntegerField(default=0)
    estimated_children_impacted = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year']
        unique_together = ('program', 'year')

    def __str__(self):
        return f"{self.program.name} - {self.year} (presencial {self.in_person_certified})"

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = CKEditor5Field('module description')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = CKEditor5Field('lesson content')
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"

