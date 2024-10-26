from django.db import models

class MetaData(models.Model):
    CATEGORY_CHOICES = [
        ('homepage', 'Página Principal'),
        ('blog', 'Blog'),
        # Agrega otras categorías si es necesario
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    keywords = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category})"

