from django.forms import ModelForm, Textarea
# validation error
from django.core.exceptions import ValidationError

from .models import CodeModel

class CodeModelForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
    class Meta:
        model=CodeModel
        widgets={"code":Textarea, "requirements":Textarea}
        exclude=["author","date"]
    def clean(self):
        author=self.initial["author"]
        # if name CodeModel with same name has been created by this user then raise ValidationError
        cms=[cm.name for cm in CodeModel.objects.filter(author=author)]
        if self.cleaned_data["name"] in cms:
            raise ValidationError("Class with same name already exists")
        return super().clean()
