from django import forms
from classroom.quicktest.models import QuickTestDefinition, QuickTestQuestion
from classroom.courses.models import Module


class QuickTestDefinitionForm(forms.ModelForm):
    class Meta:
        model = QuickTestDefinition
        fields = ["module", "title"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Module chooser: only modules without a definition, but include current instance's module
        qs = Module.objects.all()
        taken_ids = QuickTestDefinition.objects.values_list("module_id", flat=True)
        if self.instance and getattr(self.instance, "pk", None):
            qs = qs.exclude(id__in=[mid for mid in taken_ids if mid != self.instance.module_id])
        else:
            qs = qs.exclude(id__in=taken_ids)
        self.fields["module"].queryset = qs.order_by("course__title", "order")
        self.fields["module"].label_from_instance = self._module_label

    @staticmethod
    def _short(text, max_len=40):
        if not text:
            return ""
        text = str(text).strip()
        if len(text) <= max_len:
            return text
        return f"{text[: max_len - 1]}…"

    def _module_label(self, module):
        # Prioriza el nombre del modulo y acorta el curso para que se lea mejor en el select.
        module_name = self._short(module.title, max_len=52)
        course_name = self._short(getattr(module.course, "title", ""), max_len=28)
        if course_name:
            return f"{module_name}  |  {course_name}"
        return module_name


class QuickTestQuestionForm(forms.ModelForm):
    class Meta:
        model = QuickTestQuestion
        fields = [
            "text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_option",
        ]
