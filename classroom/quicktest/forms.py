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
