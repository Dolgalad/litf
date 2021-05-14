from django.contrib import admin

# Register your models here.
from .models import DataFileModel, CodeModel, ExecutionResultModel
admin.site.register(CodeModel)
admin.site.register(DataFileModel)
admin.site.register(ExecutionResultModel)
