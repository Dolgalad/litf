from django import forms

from .models import ProblemModel

from apps.codes.widgets import CodeSelectionWidget
class ProblemModelForm(forms.ModelForm):
    class Meta:
        model=ProblemModel
        exclude=["author", "date"]
        widgets={"description":forms.Textarea, "input_type":CodeSelectionWidget, "output_type":CodeSelectionWidget}

#class AddForm(forms.ModelForm):
#    class Meta:
#        model=ProblemModel
#        fields="__all__"
