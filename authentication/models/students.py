from django.db import models
from django.contrib.auth.models import User, Group  # Import Group
from .address import Address

class Students(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)
    degree = models.CharField(max_length=100)
    certifications = models.TextField(blank=True)

    def __str__(self):
        return f"students: {self.user.username}"

def assign_students_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name="students")
        instance.user.groups.add(group)

models.signals.post_save.connect(assign_students_group, sender=Students)
