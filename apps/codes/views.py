from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django import forms

# my forms
from .forms import CodeModelForm
# my models
from .models import CodeModel, DataFileModel

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
        print([k for k in fc.__dict__])
        print([k for k in fc.__dict__["_meta"].__dict__])
        #fc._meta.widgets={"code": forms.Textarea}
        print(fc._meta.widgets)
        print(self.get_form_kwargs())
        print(super().get_form_class())
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
        code_submitted_task.delay(self.object.data())
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
        print("in codemodel DetailView : post data : {}".format(request.POST))
        print("pk : {}".format(pk))
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
        context["code"]=CodeModel.objects.get(id=pk)
        print("DetailView.get_context_data : context {}".format(context))
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
        return context
    def form_valid(self, form):
        self.object=form.save()
        code_updated_task.delay(self.object.data())
        return super().form_valid(form)
        



# Data file management views
class DataAddView(CreateView):
    template_name="codes/datafile_add.html"
    model=DataFileModel
    fields="__all__"
    def get_initial(self):
        return {"date": timezone.now(), "author":self.request.user}
    def form_valid(self, form):
        print("SAVING FILE")
        self.object = form.save()
        # add the datafile object to the code
        # try getting the parent CodeModel
        if "pk" in self.kwargs:
            # adding file to a CodeModel object
            codem=CodeModel.objects.get(id=self.kwargs["pk"])
            codem.files.add(self.object)
            codem.save()
            code_updated_task.delay(codem.data())
        else:
            datafile_submitted_task.delay(self.object.data())

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
        return context
    def form_valid(self, form):
        self.object=form.save(commit=False)
        self.object.save()
        datafile_updated_task.delay(self.object.data())
        return super().form_valid(form)


class DataDetailView(TemplateView):
    template_name="codes/datafile_detail.html"
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context["file"]=DataFileModel.objects.get(id=kwargs["pk"])
        context["used_by_code"]=[cm for cm in CodeModel.objects.all() if context["file"] in cm.files.all()]
        print("FILE USED BY : {}".format(context["used_by_code"]))
        return context
