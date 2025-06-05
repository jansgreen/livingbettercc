from django.db import models

def get_user_model():
    from django.contrib.auth.models import User
    return User

User = get_user_model()

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField("Calle y casa", max_length=255)
    neighborhood = models.CharField("Barrio o sector", max_length=255)
    city = models.CharField("Municipio", max_length=100)
    province = models.CharField("Provincia", max_length=100)
    postal_code = models.CharField("Código Postal", max_length=10)

    def __str__(self):
        return f"{self.street}, {self.neighborhood} - {self.city}"
