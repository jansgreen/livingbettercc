"""
Legacy Address model moved to authentication.address app.
This module is intentionally empty to avoid accidental imports.
"""

from django.db import models

class Address(models.Model):
    # Stub para compatibilidad con migraciones viejas
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "authentication_address"  # importante si antes existía esa tabla
        managed = True
