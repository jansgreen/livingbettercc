from django import forms
from authentication.minerd.models import ReportAccountMinerd


from django import forms
from authentication.minerd.models import ReportAccountMinerd

class ReportAccountMinerdForm(forms.ModelForm):
    class Meta:
        model = ReportAccountMinerd
        fields = [
            'titulo', 'subtitulo', 'centro_educativo', 'regional', 'campos',
            'documentos', 'objetivo_razon_motivo', 'responsabilidades',
            'fecha', 'temas_impartidos'
        ]

    def __init__(self, *args, **kwargs):
        super(ReportAccountMinerdForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.fields['fecha'].widget.attrs.update({'class': 'datepicker'})
        