from django.forms import ModelForm, Textarea

from .models import CodeModel

class CodeModelForm(ModelForm):
    class Meta:
        model=CodeModel
        widgets={"code":Textarea, "requirements":Textarea}
        exclude=["author","date"]
