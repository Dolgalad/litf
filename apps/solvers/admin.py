from django.contrib import admin

from .models import SolverModel, SolverExecutionResultModel, PostprocessingResultModel
# Register your models here.
admin.site.register(SolverModel)
admin.site.register(SolverExecutionResultModel)
admin.site.register(PostprocessingResultModel)
