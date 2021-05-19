from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# import settings
from libs import settings
# import CodeModel
from apps.codes.models import DataFileModel, CodeModel, ExecutionResultModel
# Create your models here.

class ProblemModel(models.Model):
    name=models.CharField(max_length=settings.MAX_NAME_LENGTH)
    description=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateTimeField()
    input_type=models.ForeignKey(CodeModel , blank=True, on_delete=models.CASCADE, related_name="problem_input_type", null=True)
    input_data=models.ManyToManyField(DataFileModel, blank=True, related_name="problem_input_data")
    output_type=models.ForeignKey(CodeModel, blank=True, on_delete=models.CASCADE, related_name="problem_output_type",null=True)
    postprocess=models.ManyToManyField(CodeModel, blank=True, related_name="problem_postprocess")

    def get_absolute_url(self):
        return reverse("problem_detail", kwargs={"pk": self.pk})
    def __str__(self):
        return self.name
    def data(self):
        input_type_id=None
        if self.input_type:
            input_type_id=self.input_type.id
        return {"name":self.name, "description":self.description, "author":self.author.id,\
                "date":self.date, "input_type": input_type_id}


