from django import forms

from .models import ProblemModel

class ProblemModelForm(forms.ModelForm):
    class Meta:
        model=ProblemModel
        exclude=["author", "date"]
        widgets={"description":forms.Textarea}

#class AddForm(forms.ModelForm):
#    class Meta:
#        model=ProblemModel
#        fields="__all__"
