from django import forms
from authentication.minerd.models import ReportAccountMiner


class ReportAccountMinerForm(forms.ModelForm):
    class Meta:
        model = ReportAccountMiner
        fields = ['titulo', 'subtitulo', 'centro_educativo', 'regional', 'campos', 'documentos', 'prepopulated_fields', 'objetivo_razon_motivo', 'responsabilidades', 'fecha', 'temas_impartidos']
        def __init__(self, *args, **kwargs):
            super(ReportAccountMinerForm, self).__init__(*args, **kwargs)

            for field in self.fields.values():
                field.widget.attrs.update({'class': 'form-control'})
            self.fields['fecha'].widget.attrs.update({'class': 'datepicker'})
        