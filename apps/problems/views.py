from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
# my problem forms
from apps.codes.forms import CodeModelForm
from .forms import ProblemModelForm
# my models
from .models import ProblemModel
from apps.codes.models import DataFileModel, CodeModel
from apps.solvers.models import SolverModel
# debug
from libs.utils import debug_print, delete_problems, get_checked_solvers, get_checked_datafiles, delete_datafiles, delete_solvers, get_checked_postprocesses, delete_postprocesses, get_checked_problems

# tasks
from .tasks import problem_submitted_task, problem_updated_task
# Create your views here.

class DetailView(TemplateView):
    template_name="problems/detail.html"
    def post(self, request, pk):
        print("post data : {}".format(request.POST))
        if "cancel" in request.POST:
            print("CANCELING : {}".format(request.META["HTTP_REFERER"]))
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
            print("ADD POSTPROCESS")
            return HttpResponseRedirect(reverse("postprocess_add", kwargs={"pk":pk}))
        if "postprocess_delete" in request.POST:
            print("DELETE POSTPROCESS")
            ids=get_checked_postprocesses(request.POST)
            if len(ids):
                delete_postprocesses(ids, request.user)
        if "postprocess_edit" in request.POST:
            print("EDIT POSTPROCESS")
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
        print([k for k in problem.__dict__])
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
        


        return context

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
        problem_updated_task.delay(self.object.data())
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
        problem_updated_task.delay(problem.data())
        return super().form_valid(form)
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context


class PostprocessEditView(UpdateView):
    template_name="problems/postprocess_edit.html"
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
        problem_updated_task.delay(self.object.data())
        return super().form_valid(form)

   
