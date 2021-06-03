from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
# my problem forms
from apps.codes.forms import CodeModelForm
from .forms import ProblemModelForm
# my models
from .models import ProblemModel
from apps.codes.models import DataFileModel, CodeModel, ExecutionResultModel
from apps.solvers.models import SolverModel, PostprocessingResultModel, SolverExecutionResultModel
# debug
from libs.utils import debug_print, delete_problems, get_checked_solvers, get_checked_datafiles, delete_datafiles, delete_solvers, get_checked_postprocesses, delete_postprocesses, get_checked_problems

# tasks
from .tasks import problem_submitted_task, problem_updated_task, postprocess_updated_task

from wsgiref.util import FileWrapper

import os
from io import BytesIO, StringIO
# Create your views here.

class DetailView(TemplateView):
    template_name="problems/detail.html"
    def post(self, request, pk):
        if "cancel" in request.POST:
            return HttpResponseRedirect(request.META["HETTP_REFERER"])
        if "datafile_add" in request.POST:
            return HttpResponseRedirect(reverse("problem_datafile_add", kwargs={"pk":pk}))
        if "datafile_edit" in request.POST:
            ids=get_checked_datafiles(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("You have selected {} items for editing, editing the first : {}".format(len(ids), ids[0]))
                return HttpResponseRedirect(reverse("datafile_edit", kwargs={"pk":ids[0]}))
        if "datafile_delete" in request.POST:
            ids=get_checked_datafiles(request.POST)
            if len(ids):
                delete_datafiles(ids, request.user)
        if "solver_add" in request.POST:
            return HttpResponseRedirect(reverse("solver_add", kwargs={"problem_id":pk}))
        if "solver_edit" in request.POST:
            ids=get_checked_solvers(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("You have selected {} items for editing, editing the first :{}".format(len(ids), ids[0]))
                return HttpResponseRedirect(reverse("solver_edit", kwargs={"pk":ids[0]}))
        if "solver_delete" in request.POST:
            ids=get_checked_solvers(request.POST)
            delete_solvers(ids, request.user)

        if "postprocess_add" in request.POST:
            return HttpResponseRedirect(reverse("postprocess_add", kwargs={"pk":pk}))
        if "postprocess_delete" in request.POST:
            ids=get_checked_postprocesses(request.POST)
            if len(ids):
                delete_postprocesses(ids, request.user)
        if "postprocess_edit" in request.POST:
            ids=get_checked_postprocesses(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("You have select {} items for editing , editing the first {}".format(len(ids), ids[0]))
                return HttpResponseRedirect(reverse("postprocess_edit", kwargs={"pk":ids[0]}))
        return HttpResponseRedirect(reverse("problem_detail", kwargs={"pk":pk}))
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        problem=ProblemModel.objects.get(id=kwargs["pk"])
        context["problem"]=problem
        context["files"]=problem.input_data.all()
        context["solvers"]=SolverModel.objects.filter(problem=problem)
        context["postprocesses"]=problem.postprocess.all()
        # permissions
        context["datafile_add_permission"]=(self.request.user.is_superuser or \
                                            self.request.user.is_authenticated)
        context["datafile_edit_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        context["datafile_delete_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        context["solver_add_permission"]=(self.request.user.is_superuser or \
                                            self.request.user.is_authenticated)
        context["solver_edit_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        context["solver_delete_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        context["postprocess_add_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        context["postprocess_edit_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        context["postprocess_delete_permission"]=(self.request.user.is_superuser or \
                                            self.request.user == problem.author)
        
        # get list of solutions
        context["solutions"]=self.get_solutions(problem)

        return context
    def get_solutions(self,problem):
        # get solvers
        solvers=SolverModel.objects.filter(problem=problem)
        if len(solvers)==0:
            return []
        # get solutions for each of these solvers
        s=[]
        for solver in solvers:
            t_s=SolverExecutionResultModel.objects.filter(solver=solver)
            # get the post processing results for each solution
            t_p=[]
            for sol in t_s:
                t_p.append(PostprocessingResultModel.objects.filter(execution_result=sol.result))
                s.append((sol, t_p[-1]))
        return s

class IndexView(TemplateView):
    template_name="problems/index.html"
    def post(self, request):
        debug_print("in problems.views.IndexView.post : {}".format(request.POST))
        if "problem_add" in request.POST:
            return HttpResponseRedirect(reverse("problem_add"))
        if "problem_edit" in request.POST:
            ids=get_checked_problems(request.POST)
            return HttpResponseRedirect(reverse("problem_edit", kwargs={"pk":ids[0]}))
        if "problem_delete" in request.POST:
            # delete the problems
            ids=[int(k.replace("problem_id_","")) for k in request.POST if k.startswith("problem_id_")]
            delete_problems(ids, user=request.user)
        return HttpResponseRedirect(reverse("problem_index"))
    def get_context_data(self):
        context=super().get_context_data()
        context["problems"]=ProblemModel.objects.all()
        return context

class AddView(CreateView):
    template_name="problems/add.html"
    model=ProblemModel
    form_class=ProblemModelForm
    def get_initial(self):
        return {"author":self.request.user, "date":timezone.now()}
    def get_form_kwargs(self, *args, **kwargs):
        kwargs=super().get_form_kwargs(*args,**kwargs)
        return kwargs
    def is_valid(self, *args, **kwargs):
        return super().is_valid(*args, **kwargs)
    def form_valid(self,form):
        self.object=form.save(commit=False)
        self.object.date=timezone.now()
        self.object.author=self.request.user
        self.object.save()
        problem_submitted_task.delay(self.object.data())
        return super().form_valid(form)
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context

class EditView(UpdateView):
    model=ProblemModel
    template_name="problems/edit.html"
    form_class=ProblemModelForm
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context
    def form_valid(self, form):
        self.object=form.save()
        problem_updated_task.delay(self.object.id)
        return super().form_valid(form)

class DataAddView(CreateView):
    template_name="codes/datafile_add.html"
    model=DataFileModel
    fields="__all__"
    def get_initial(self):
        return {"date":timezone.now(), "author":self.request.user}
    def form_valid(self, form):
        self.object=form.save()
        # add the datafile to the problem
        problem=ProblemModel.objects.get(id=self.kwargs["pk"])
        problem.input_data.add(self.object)
        problem.save()
        return super().form_valid(form)
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context


class PostprocessAddView(CreateView):
    template_name="codes/add.html"
    model=CodeModel
    form_class=CodeModelForm
    def get_initial(self):
        return {"date":timezone.now(), "author":self.request.user}
    def form_valid(self, form):
        self.object=form.save(commit=False)
        self.object.author=self.request.user
        self.object.date=timezone.now()
        self.object.save()
        # add the postprocessing object to the ProblemModel
        problem=ProblemModel.objects.get(id=self.kwargs["pk"])
        problem.postprocess.add(self.object)
        problem.save()
        problem_updated_task.delay(problem.id)
        return super().form_valid(form)
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context


class PostprocessEditView(UpdateView):
    #template_name="problems/postprocess_edit.html"
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
        #problem_updated_task.delay(self.object.data())
        postprocess_updated_task.delay(self.object.id)
        return super().form_valid(form)
    def get_initial(self):
        context=super().get_initial()
        context["author"]=self.request.user
        return context


class AboutView(TemplateView):
    template_name="about.html"

def getsize(f):
    p=f.tell()
    f.seek(0,os.SEEK_END)
    s=f.tell()
    f.seek(p)
    return s

def postprocess_output_download_view(request, pk):
    file_content=PostprocessingResultModel.objects.get(id=pk).output_data
    # file content in bytes
    if isinstance(file_content, bytes):
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


