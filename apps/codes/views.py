from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django import forms

import json
import tempfile
import os
from io import StringIO, BytesIO
from wsgiref.util import FileWrapper

# my forms
from .forms import CodeModelForm
# my models
from .models import CodeModel, DataFileModel, ExecutionResultModel

# tasks
from .tasks import code_submitted_task, code_updated_task, datafile_submitted_task, datafile_updated_task

from libs.utils import get_checked_datafiles, delete_datafiles
# Create your views here.

class AddView(CreateView):
    template_name="codes/add.html"
    model=CodeModel
    form_class=CodeModelForm
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)
    def get_form_class(self, *args, **kwargs):
        fc=super().get_form_class(*args,**kwargs)
        #fc._meta.widgets={"code": forms.Textarea}
        return fc
    def get_form(self, *args, **kwargs):
        return super().get_form(*args,**kwargs)
    def post(self, *args, **kwargs):
        return super().post(*args,**kwargs)
    def get_initial(self):
        return {"author":self.request.user,"date":timezone.now()}
    def form_valid(self, form):
        self.object=form.save(commit=False)
        self.object.author=self.request.user
        self.object.date=timezone.now()
        self.object.save()
        code_submitted_task.delay(self.object.id)
        return super().form_valid(form)
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context


class DetailView(TemplateView):
    template_name="codes/detail.html"
    def post(self,request,pk):
        if "datafile_add" in request.POST:
            return HttpResponseRedirect(reverse("code_datafile_add", kwargs={"pk":pk}))
        if "datafile_edit" in request.POST:
            ids=get_checked_datafiles(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("You have selected {} for editing, editing the first : {}".format(len(ids), ids[0]))
                return HttpResponseRedirect(reverse("datafile_edit", kwargs={"pk":ids[0]}))
        if "datafile_delete" in request.POST:
            ids=get_checked_datafiles(request.POST)
            delete_datafiles(ids, request.user)
        return HttpResponseRedirect(reverse("code_detail", kwargs={"pk":pk}))
    def get_context_data(self,**kwargs):
        pk=kwargs["pk"]
        context=super().get_context_data(**kwargs)
        cm=CodeModel.objects.get(id=pk)
        context["code"]=cm
        if not cm.requirements is None:
            context["requirements"]=str(cm.requirements).split("\n")
        er=cm.get_execution_results()
        if len(er):
            context["execution_results"]=er
        if not cm.arguments is None:
            ad=json.loads(cm.arguments.data)
            context["argument_description"]=ad
            context["pos_argument_description"]=ad["args"]
            context["kw_argument_description"]=ad["kwargs"]
        return context

class EditView(UpdateView):
    template_name="codes/edit.html"
    model=CodeModel
    form_class=CodeModelForm
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        if "_popup" in self.request.GET:
            context["popup"]=True
        else:
            context["popup"]=False
        return context
    def form_valid(self, form):
        self.object=form.save()
        code_updated_task.delay(self.object.id)
        return super().form_valid(form)
    def get_form_kwargs(self):
        a=super().get_form_kwargs()
        return a
    def get_initial(self):
        context=super().get_initial()
        context["author"]=self.request.user
        return context
    def get(self, *args, **kwargs):
        return super().get(*args,**kwargs)
        



# Data file management views
class DataAddView(CreateView):
    template_name="codes/datafile_add.html"
    model=DataFileModel
    fields="__all__"
    def get_initial(self):
        return {"date": timezone.now(), "author":self.request.user}
    def form_valid(self, form):
        self.object = form.save()
        # add the datafile object to the code
        # try getting the parent CodeModel
        if "pk" in self.kwargs:
            # adding file to a CodeModel object
            codem=CodeModel.objects.get(id=self.kwargs["pk"])
            codem.files.add(self.object)
            codem.save()
            code_updated_task.delay(codem.id)
        else:
            datafile_submitted_task.delay(self.object.id)

        return HttpResponseRedirect(self.get_success_url())
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context


class DataEditView(UpdateView):
    template_name="codes/datafile_edit.html"
    model=DataFileModel
    fields="__all__"
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")

        # DEBUG - remove this pls
        from django.forms import modelformset_factory
        mfsf=modelformset_factory(CodeModel, fields="__all__", extra=1)
        context["formset"]=mfsf(queryset=CodeModel.objects.filter(id=10))
        #context["formset"]=mfsf()
        return context
    def form_valid(self, form):
        self.object=form.save(commit=False)
        self.object.save()
        datafile_updated_task.delay(self.object.id)
        return super().form_valid(form)


class DataDetailView(TemplateView):
    template_name="codes/datafile_detail.html"
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context["file"]=DataFileModel.objects.get(id=kwargs["pk"])
        context["used_by_code"]=[cm for cm in CodeModel.objects.all() if context["file"] in cm.files.all()]
        return context

def getsize(f):
    p=f.tell()
    f.seek(0,os.SEEK_END)
    s=f.tell()
    f.seek(p)
    return s
def output_download_view(request,exe_id):
    file_content=ExecutionResultModel.objects.get(id=exe_id).output_data
    # file content in bytes
    if isinstance(file_content, bytes):
        try:
            f=StringIO(file_content.decode("utf-8"))
        except:
            f=BytesIO(file_content)
    else:
        f=StringIO(file_content)
    s=getsize(f)
    wrapper=FileWrapper(f)
    #response=HttpResponse(wrapper, content_type="text/plain")
    response=HttpResponse(wrapper, content_type="text/plain")
    response["Content-Disposition"]="attachement; filename=output"
    response["Content-Length"]=s
    return response

def stderr_download_view(request,exe_id):
    file_content=ExecutionResultModel.objects.get(id=exe_id).errors
    # file content in bytes
    f=StringIO(file_content)
    s=getsize(f)
    wrapper=FileWrapper(f)
    #response=HttpResponse(wrapper, content_type="text/plain")
    response=HttpResponse(wrapper, content_type="text/plain")
    response["Content-Disposition"]="attachement; filename=output"
    response["Content-Length"]=s
    return response

def stdout_download_view(request,exe_id):
    file_content=ExecutionResultModel.objects.get(id=exe_id).stdout
    f=StringIO(file_content)
    s=getsize(f)
    wrapper=FileWrapper(f)
    #response=HttpResponse(wrapper, content_type="text/plain")
    response=HttpResponse(wrapper, content_type="text/plain")
    response["Content-Disposition"]="attachement; filename=output"
    response["Content-Length"]=s
    return response


