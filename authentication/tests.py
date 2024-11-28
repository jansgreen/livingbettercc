from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile
from .forms import Profileforms

class ProfileFunctionTest(TestCase):
    def setUp(self):
        # Crear un cliente para simular solicitudes
        self.client = Client()

        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(
            username='testuser', 
            password='password123', 
            first_name='Test', 
            last_name='User'
        )

        # URL de la vista que vamos a probar
        self.url = reverse('ProfileFunction')  # Ajusta este nombre a tu URL real

    def test_profile_creation(self):
        # Inicia sesión como el usuario
        self.client.login(username='testuser', password='password123')

        # Asegurarse de que no existe un perfil inicialmente
        self.assertFalse(Profile.objects.filter(user=self.user).exists())

        # Realizar una solicitud GET
        response = self.client.get(self.url)

        # Asegurarse de que se haya creado un perfil automáticamente
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

    def test_profile_update_post(self):
        # Inicia sesión como el usuario
        self.client.login(username='testuser', password='password123')

        # Datos POST para actualizar el perfil
        data = {
            'firstname': 'UpdatedFirstName',
            'lastname': 'UpdatedLastName',
            'provincia': 'Provincia1',
            'municipios': 'Municipio1',
            'zip': '12345',
        }

        # Realizar una solicitud POST
        response = self.client.post(self.url, data)

        # Verificar redirección después de un guardado exitoso
        self.assertRedirects(response, self.url)

        # Verificar que los datos del usuario se han actualizado
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedFirstName')
        self.assertEqual(self.user.last_name, 'UpdatedLastName')

        # Verificar que los datos del perfil se han actualizado
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.provincia, 'Provincia1')
        self.assertEqual(profile.municipio, 'Municipio1')
        self.assertEqual(profile.codigo_postal, '12345')

    def test_profile_form_invalid(self):
        # Inicia sesión como el usuario
        self.client.login(username='testuser', password='password123')

        # Datos POST inválidos
        data = {
            'firstname': '',  # Nombre vacío, suponiendo que sea requerido
            'lastname': '',
        }

        # Realizar una solicitud POST
        response = self.client.post(self.url, data)

        # Verificar que no hay redirección, el formulario es inválido
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'first_name', 'Este campo es obligatorio.')  # Ajusta según tus validaciones

    def test_get_request_with_existing_profile(self):
        # Crear un perfil asociado al usuario
        Profile.objects.create(user=self.user)

        # Inicia sesión como el usuario
        self.client.login(username='testuser', password='password123')

        # Realizar una solicitud GET
        response = self.client.get(self.url)

        # Asegurarse de que la página cargue correctamente
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

        # Verificar que el formulario contiene datos del perfil existente
        form = response.context['form']
        self.assertEqual(form.instance.user, self.user)
