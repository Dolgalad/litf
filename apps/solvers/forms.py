from django import forms

from .models import SolverModel

class SolverModelForm(forms.ModelForm):
    class Meta:
        model=SolverModel
        widgets={"description":forms.Textarea}
        exclude=["author","date","problem"]
