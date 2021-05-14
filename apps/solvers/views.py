from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.utils import timezone
# my forms
from .forms import SolverModelForm
# my models 
from .models import SolverModel
from apps.problems.models import ProblemModel

# tasks
from .tasks import solver_submitted_task, solver_updated_task
# Create your views here.

class DetailView(TemplateView):
    template_name="solvers/detail.html"
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context["solver"]=SolverModel.objects.get(id=kwargs["pk"])
        return context

class AddView(CreateView):
    template_name="solvers/add.html"
    model=SolverModel
    form_class=SolverModelForm
    def get_initial(self):
        print("KWARGS : {}".format(self.kwargs))
        return {"date":timezone.now(), "author":self.request.user, "problem":ProblemModel.objects.get(id=self.kwargs["problem_id"])}
    def form_valid(self,form):
        self.object=form.save(commit=False)
        self.object.author=self.request.user
        self.object.date=timezone.now()
        self.object.problem=ProblemModel.objects.get(id=self.kwargs["problem_id"])
        self.object.save()
        solver_submitted_task.delay(self.object.data())
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context

class EditView(UpdateView):
    template_name="solvers/edit.html"
    model=SolverModel
    form_class=SolverModelForm
    def form_valid(self, form):
        self.object=form.save(commit=False)
        self.object.save()
        solver_updated_task.delay(self.object.data())
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        if "HTTP_REFERER" in self.request.META:
            context["cancel_url"]=self.request.META["HTTP_REFERER"]
        else:
            context["cancel_url"]=reverse("profile")
        return context



