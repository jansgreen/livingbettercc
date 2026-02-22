from django.test import TestCase
from django.contrib.auth.models import Group, Permission
from .forms import GroupForm, PermissionForm, InviteForm

class GroupFormTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # Crear algunos grupos para probar
        Group.objects.create(name='Admin')
        Group.objects.create(name='User')

    def test_group_form_valid_data(self):
        form = GroupForm(data={'group': Group.objects.first().id})
        self.assertTrue(form.is_valid())

    def test_group_form_invalid_data(self):
        form = GroupForm(data={'group': 999})  # Grupo que no existe
        self.assertFalse(form.is_valid())

    def test_group_form_empty_data(self):
        form = GroupForm(data={})
        self.assertFalse(form.is_valid())

class PermissionFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crear algunos permisos para probar
        cls.permission1 = Permission.objects.create(codename='perm1', name='Permission 1', content_type_id=1)
        cls.permission2 = Permission.objects.create(codename='perm2', name='Permission 2', content_type_id=1)

    def test_permission_form_valid_data(self):
        form = PermissionForm(data={'permissions': [self.permission1.id, self.permission2.id]})
        self.assertTrue(form.is_valid())

    def test_permission_form_invalid_data(self):
        form = PermissionForm(data={'permissions': [999]})  # Permiso que no existe
        self.assertFalse(form.is_valid())

    def test_permission_form_empty_data(self):
        form = PermissionForm(data={})
        self.assertFalse(form.is_valid())

class InviteFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crear un grupo para la prueba
        cls.group = Group.objects.create(name='Test Group')

    def test_invite_form_valid_data(self):
        form = InviteForm(data={'email': 'test@example.com', 'group': self.group.id})
        self.assertTrue(form.is_valid())

    def test_invite_form_invalid_email(self):
        form = InviteForm(data={'email': 'invalid-email', 'group': self.group.id})
        self.assertFalse(form.is_valid())

    def test_invite_form_empty_data(self):
        form = InviteForm(data={})
        self.assertFalse(form.is_valid())
