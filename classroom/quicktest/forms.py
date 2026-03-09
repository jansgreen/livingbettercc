from django import forms

from classroom.courses.models import Module
from classroom.quicktest.models import QuickTestDefinition, QuickTestQuestion


class QuickTestDefinitionForm(forms.ModelForm):
    class Meta:
        model = QuickTestDefinition
        fields = ["module", "title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Module.objects.all()
        taken_ids = QuickTestDefinition.objects.values_list("module_id", flat=True)
        if self.instance and getattr(self.instance, "pk", None):
            qs = qs.exclude(id__in=[mid for mid in taken_ids if mid != self.instance.module_id])
        else:
            qs = qs.exclude(id__in=taken_ids)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        self.fields["module"].widget.attrs.update({"class": "form-select form-select-lg mb-3"})
        self.fields["module"].queryset = qs.order_by("course__title", "order")
        self.fields["module"].label_from_instance = self._module_label

    @staticmethod
    def _short(text, max_len=40):
        if not text:
            return ""
        text = str(text).strip()
        if len(text) <= max_len:
            return text
        return f"{text[: max_len - 1]}..."

    def _module_label(self, module):
        module_name = self._short(module.title, max_len=52)
        course_name = self._short(getattr(module.course, "title", ""), max_len=28)
        if course_name:
            return f"{module_name}  |  {course_name}"
        return module_name


class QuickTestQuestionForm(forms.ModelForm):
    class Meta:
        model = QuickTestQuestion
        fields = [
            "question_type",
            "text",
            "expected_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["question_type"].widget.attrs.update({"class": "form-select form-select-lg mb-3"})
        self.fields["question_type"].initial = (
            self.instance.question_type
            if self.instance and getattr(self.instance, "pk", None)
            else QuickTestQuestion.QuestionType.MULTIPLE_CHOICE
        )
        self.fields["question_type"].help_text = "Selecciona el tipo: selección múltiple, respuesta escrita o firma."
        self.fields["text"].label = "Texto de la pregunta"
        self.fields["text"].widget = forms.Textarea(
            attrs={"class": "form-control", "rows": 3, "placeholder": "Inserta la pregunta"}
        )
        self.fields["expected_text"].label = "Respuesta esperada (opcional para respuesta escrita)"
        self.fields["expected_text"].widget = forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Opcional. Si esta vacio, se valida que el usuario escriba algo.",
            }
        )

        for name, field in self.fields.items():
            if name in {"question_type", "text", "expected_text"}:
                continue
            if name == "correct_option":
                field.widget = forms.Select(
                    attrs={"class": "form-select"},
                    choices=[
                        ("", "Seleccione opcion correcta"),
                        ("A", "Opcion A"),
                        ("B", "Opcion B"),
                        ("C", "Opcion C"),
                        ("D", "Opcion D"),
                    ],
                )
            else:
                field.widget = forms.TextInput(attrs={"class": "form-control"})

    def clean(self):
        cleaned = super().clean()
        qtype = cleaned.get("question_type")

        if qtype == QuickTestQuestion.QuestionType.MULTIPLE_CHOICE:
            for field in ("option_a", "option_b", "option_c", "option_d", "correct_option"):
                if not str(cleaned.get(field, "")).strip():
                    self.add_error(field, "Este campo es obligatorio para seleccion multiple.")
        else:
            cleaned["option_a"] = ""
            cleaned["option_b"] = ""
            cleaned["option_c"] = ""
            cleaned["option_d"] = ""
            cleaned["correct_option"] = ""

        if qtype == QuickTestQuestion.QuestionType.SIGNATURE:
            cleaned["expected_text"] = ""

        return cleaned
