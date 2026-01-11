from django import forms
from .models import Certificate

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
