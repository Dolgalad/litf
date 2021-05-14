from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# import general settings for this project
from libs import settings
# import some errors
from libs import errors
# Create your models here.

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
    dependencies=models.ManyToManyField("self", blank=True, related_name="code_dependencies")
    files=models.ManyToManyField(DataFileModel, blank=True, related_name="code_files")
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateTimeField()
    
    def get_absolute_url(self):
        return reverse("code_detail", kwargs={"pk": self.pk})
    def dependency_count(self):
        """Return number of dependencies
        :return: number of dependencies of this object
        :rtype: int
        """
        return len(self.dependencies.all())
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
    def __str__(self):
        return self.name
    def data(self):
        return {"name":self.name, "code":self.code, "requirements":self.requirements, \
                "dependencies":[dep.data() for dep in self.dependencies.all()], \
                "files":[f.path for f in self.files.all()], "author":self.author.id, \
                "date":self.date}
class ExecutionResultModel(models.Model):
    implementation=models.ForeignKey(CodeModel, on_delete=models.CASCADE)
    input_data=models.ForeignKey(DataFileModel, on_delete=models.CASCADE)
    output_data=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    status=models.IntegerField(default=1)
    start_time=models.DateTimeField()
    stop_time=models.DateTimeField()
    stdout=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    errors=models.CharField(max_length=settings.MAX_TEXT_LENGTH, blank=True, null=True)
    def data(self):
        return {"implementation":self.implementation.id, "input_data":self.input_data.id,\
                "output_data":self.output_data, "status":self.status, "start_time":start_time,\
                "stop_time":self.stop_time, "stdout":self.stdout, "errors":self.errors}