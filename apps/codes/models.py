from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# import general settings for this project
from libs import settings
# import some errors
from libs import errors
# import code execution status
from libs.code import status
# Create your models here.

class CodeArgumentModel(models.Model):
    data=models.CharField(max_length=settings.MAX_TEXT_LENGTH)

class DataFileModel(models.Model):
    datafile=models.FileField(upload_to="data")
    flags=models.CharField(blank=True, null=True, max_length=settings.MAX_FLAGS_LENGTH)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateTimeField()
    def get_absolute_url(self):
        return reverse("datafile_detail", kwargs={"pk": self.pk})
    def __str__(self):
        return self.datafile.name
    def data(self):
        return {"datafile": self.datafile.path, "flags":self.flags, "author":self.author.id, \
                "date":self.date}

class CodeModel(models.Model):
    name=models.CharField(max_length=settings.MAX_NAME_LENGTH)
    code=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    requirements=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    dependencies=models.ManyToManyField("self", symmetrical=False,blank=True, related_name="code_dependencies")
    files=models.ManyToManyField(DataFileModel, blank=True, related_name="code_files")
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateTimeField()
    status=models.IntegerField(default=-1)
    arguments=models.ForeignKey(CodeArgumentModel, blank=True, null=True, on_delete=models.CASCADE)
    def get_dependants(self):
        a=[]
        for c in CodeModel.objects.all():
            if c.depends(self):
                if not c in a:
                    a.append(c)
        return a
    def depends(self, d):
        return d in self.dependencies.all()
    def get_execution_results(self):
        return ExecutionResultModel.objects.filter(implementation=self)
    def get_absolute_url(self):
        return reverse("code_detail", kwargs={"pk": self.pk})
    def dependency_count(self):
        """Return number of dependencies
        :return: number of dependencies of this object
        :rtype: int
        """
        return len(self.dependencies.all())
    def file_count(self):
        return len(self.files.all())
    def get_requirements(self):
        """Get the requirements for this object, checks all dependencies for dependencies and returns the full list
        :return: requirements list
        :rtype: list of str objects
        """
        a=[]
        if self.dependency_count():
            for dep in self.dependencies.all():
                for r in dep.get_requirements():
                    if not r in a:
                        a.append(r)
        if self.requirements:
            for r in self.requirements.split("\n"):
                if len(r) and (not r in a):
                    a.append(r)
        return a

    def get_code(self):
        """Get the code for this model, if this object has dependencies their code will be prefixed
        
        :return: declaration code for this object
        :rtype: str
        """
        a=""
        if self.dependency_count():
            for dep in self.dependencies.all():
                a+=dep.get_code()+"\n"
        if self.code_empty():
            print(errors.CODEMODEL_CODE_EMPTY)
            return a
        return a+self.code
    def get_filenames(self):
        a=[]
        if self.dependency_count():
            for dep in self.dependencies.all():
                for f in dep.get_filenames():
                    if not f in a:
                        a.append(f)
        if self.file_count():
            for f in self.files.all():
                if not f.datafile.path in a:
                    a.append(f.datafile.path)
        return a
    def code_empty(self):
        return len(self.code)==0
    def __str__(self):
        return self.name
    def data(self):
        return {"name":self.name, "code":self.code, "requirements":self.requirements, \
                "dependencies":[dep.data() for dep in self.dependencies.all()], \
                "files":[f.datafile.path for f in self.files.all()], "author":self.author.id, \
                "date":self.date}
    def get_execution_results(self):
        return ExecutionResultModel.objects.filter(implementation=self)
    def get_pending_execution_result(self):
        for exec_res in self.get_execution_results():
            if exec_res.status==status.ExecutionStatus.PENDING:
                return exec_res
    def has_pending_execution_result(self):
        a=self.get_pending_execution_result()
        return not a is None
    def create_pending_execution_result(self):
        ep=ExecutionResultModel.objects.create(implementation=self,status=status.ExecutionStatus.PENDING)
        ep.save()

class ExecutionResultModel(models.Model):
    implementation=models.ForeignKey(CodeModel, on_delete=models.CASCADE)
    input_data=models.ForeignKey(DataFileModel, on_delete=models.CASCADE, blank=True, null=True)
    output_data=models.BinaryField(blank=True, null=True)
    output_type=models.CharField(max_length=settings.MAX_NAME_LENGTH, blank=True, null=True)
    status=models.IntegerField(default=-1)
    start_time=models.DateTimeField(blank=True,null=True)
    stop_time=models.DateTimeField(blank=True,null=True)
    stdout=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    errors=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    flags=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    def data(self):
        a= {"implementation":self.implementation.id, "input_data":None,\
                "output_data":None, "status":self.status, "start_time":self.start_time,\
                "stop_time":self.stop_time, "stdout":self.stdout, "errors":self.errors, "flags":self.flags}
        if self.input_data:
            a["input_data"]=self.input_data.id
        if self.output_data:
            a["output_data"]=self.output_data
        return a
    def __str__(self):
        return "ExecutionResultModel : status : {}".format(self.status)
    def set_pending(self):
        self.output_data=None
        self.start_time=None
        self.stop_time=None
        self.status=status.ExecutionStatus.PENDING
        self.errors=None
        self.stdout=None
        self.save()
