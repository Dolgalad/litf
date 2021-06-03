from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# import project common settings
from libs import settings

# import execution states
from libs.code import status

# import CodeModel and DataFileModel
from apps.codes.models import CodeModel, DataFileModel, ExecutionResultModel
# import ProblemModel
from apps.problems.models import ProblemModel

import pickle as pkl
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
    def html_link_detail(self):
        return "<a href=\"{}\">{}</a>".format(reverse("solver_detail",self.pk), self.name)
    def get_execution_results(self):
        return SolverExecutionResultModel.objects.filter(solver=self)
    def get_pending_execution_result(self):
        for exec_res in self.get_execution_results():
            if exec_res.status==status.CodeExecutionStatus.PENDING:
                return exec_res
    def has_pending_execution_result(self):
        e=self.get_pending_execution_result()
        return not e is None
    def create_pending_execution_result(self):
        SolverExecutionResultModel.objects.create(solver=self,status=status.CodeExecutionStatus.PENDING)

class SolverExecutionResultModel(models.Model):
    solver=models.ForeignKey(SolverModel, on_delete=models.CASCADE)
    status=models.IntegerField(default=-1)
    result=models.ForeignKey(ExecutionResultModel, blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return "SolverExecutionResultModel : status : {}".format(self.status)


class PostprocessingResultModel(models.Model):
    problem=models.ForeignKey(ProblemModel, on_delete=models.CASCADE)
    solver=models.ForeignKey(SolverModel, on_delete=models.CASCADE)
    implementation=models.ForeignKey(CodeModel, on_delete=models.CASCADE)
    output_data=models.BinaryField(blank=True, null=True)
    output_type=models.CharField(blank=True , null=True, default="float", max_length=settings.MAX_TEXT_LENGTH)
    output_file=models.FileField(blank=True, upload_to="postprocessing")
    # postprocessing is linked to an execution result
    execution_result=models.ForeignKey(ExecutionResultModel, on_delete=models.CASCADE)
    def html_render(self):
        if not self.output_data is None:
            print("type : {}".format(self.output_type))
            # check type 
            if self.output_type!="<class 'bytes'>":
                if isinstance(self.output_data, bytes):
                    return pkl.loads(self.output_data)
                return self.output_data
            else:
                print("output type : {}".format(self.output_type))
                print("output data : {}".format(self.output_data))
                return "<a href='/problem/postprocess_output/{}/'>(output)</a>".format(self.pk)
            return str(self.output_data)
        if not self.output_file is None:
            try:
                return "<a href=\"{}\"><img height=\"50\" width=\"50\" src=\"{}\"></a>".format(self.output_file.url,self.output_file.url)
            except:
                return "fail"
        return "AAA"
