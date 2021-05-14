from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# import project common settings
from libs import settings
# import CodeModel and DataFileModel
from apps.codes.models import CodeModel, DataFileModel
# import ProblemModel
from apps.problems.models import ProblemModel

# Create your models here.

class SolverModel(models.Model):
    name=models.CharField(max_length=settings.MAX_NAME_LENGTH)
    implementation=models.ForeignKey(CodeModel, on_delete=models.CASCADE)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateTimeField()
    description=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    problem=models.ForeignKey(ProblemModel, on_delete=models.CASCADE)
    def get_absolute_url(self):
        return reverse("solver_detail", kwargs={"pk":self.pk})
    def __str__(self):
        return self.name
    def data(self):
        return {"name":self.name, "implementation":self.implementation.id, "author":self.author.id,\
                "date":self.date,"description":self.description, "problem":self.problem.id}
