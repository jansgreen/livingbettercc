from django import forms
from .models import Certificate, BecadoCertificateRequest

class CertificateForm(forms.ModelForm):
	class Meta:
		model = Certificate
		fields = ["user", "course", "issued_date"]
		widgets = {
			"issued_date": forms.DateInput(attrs={"type": "date"}),
		}

	def clean(self):
		cleaned = super().clean()
		# Enforce unique user + course per model constraint with a user-friendly error
		user = cleaned.get("user")
		course = cleaned.get("course")
		if user and course:
			qs = Certificate.objects.filter(user=user, course=course)
			# Exclude current instance on update
			if self.instance and self.instance.pk:
				qs = qs.exclude(pk=self.instance.pk)
			if qs.exists():
				raise forms.ValidationError("Este usuario ya tiene certificado para este curso.")
		return cleaned


class BecadoCertificateRequestForm(forms.ModelForm):
	class Meta:
		model = BecadoCertificateRequest
		fields = [
			"full_name",
			"educational_center",
			"regional",
			"email",
			"phone",
		]
		labels = {
			"full_name": "Nombre completo",
			"educational_center": "Centro educativo",
			"regional": "Regional",
			"email": "Correo electrónico",
			"phone": "Número de teléfono",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		for name, field in self.fields.items():
			field.widget.attrs["class"] = "form-control"
			if name in {"full_name", "educational_center", "regional"}:
				field.widget.attrs["placeholder"] = field.label
			if name == "email":
				field.widget.attrs["placeholder"] = "nombre@correo.com"
			if name == "phone":
				field.widget.attrs["placeholder"] = "809-000-0000"
