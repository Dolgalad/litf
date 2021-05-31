from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponsePermanentRedirect
from django.urls import reverse
# user authentification
from django.contrib.auth import login, logout, authenticate

# import models
from django.contrib.auth.models import User
from apps.problems.models import ProblemModel
from apps.codes.models import CodeModel, DataFileModel

# import my forms
from .forms import LoginForm, RegistrationForm

# debug and usefull
from libs.utils import delete_problems, delete_codes, get_checked_problems, get_checked_codes, debug_print, get_checked_datafiles, delete_datafiles
# Create your views here.
class LoginView(FormView):
    template_name="users/login.html"
    form_class=LoginForm
    success_url="/profile"
    def post(self, request):
        if "register" in request.POST:
            return HttpResponseRedirect(reverse("register"))
        form=self.form_class(request.POST)
        if self.form_valid(form):
            username=request.POST["username"]
            password=request.POST["password"]
            user=authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("In LoginView.post : just before redirect")
                return HttpResponseRedirect(reverse("profile"))
        else:
            print("WARNING : authenticate failed : {}".format(request.POST))
        return HttpResponseRedirect(reverse("login"))
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("profile"))
        return super().get(request)

class RegistrationView(FormView):
    template_name="users/register.html"
    form_class=RegistrationForm
    success_url="/profile"
    def form_valid(self, form):
        username=form.cleaned_data["username"]
        password=form.cleaned_data["password"]
        pwd_conf=form.cleaned_data["password_confirm"]
        email=form.cleaned_data["email"]
        if username and (password==pwd_conf):
            user=User.objects.create_user(username=username,\
                    password=password,\
                    email=pwd_conf)
            user.save()
            # authenticate the user
            user=authenticate(self.request, username=username, password=password)
            if not user is None:
                login(self.request, user)
                return HttpResponseRedirect(reverse("profile"))
            else:
                return HttpResponseRedirect(reverse("login"))
        return super().form_valid(form)

class ProfileView(TemplateView):
    template_name="users/profile.html"
    def post(self, request):
        debug_print("in apps.users.views.ProfileView : {}".format(request.POST))
        if "problem_add" in request.POST:
            return HttpResponseRedirect(reverse("problem_add"))
        if "problem_delete" in request.POST:
            ids=get_checked_problems(request.POST)
            delete_problems(ids, user=request.user)
        if "problem_edit" in request.POST:
            ids=get_checked_problems(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("More then 1 problem id provided for editing, editing first : {}".format(ids[0]))

                return HttpResponseRedirect(reverse("problem_edit", kwargs={"pk":ids[0]}))
        if "code_add" in request.POST:
            return HttpResponseRedirect(reverse("code_add"))
        if "code_delete" in request.POST:
            ids=get_checked_codes(request.POST)
            delete_codes(ids, user=request.user)
        if "code_edit" in request.POST:
            ids=get_checked_codes(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("More then 1 code id provided for editing, editing first : {}".format(ids[0]))
                return HttpResponseRedirect(reverse("code_edit" , kwargs={"pk":ids[0]}))
        if "datafile_add" in request.POST:
            return HttpResponseRedirect(reverse("datafile_add"))
        if "datafile_edit" in request.POST:
            ids=get_checked_datafiles(request.POST)
            if len(ids):
                if len(ids)>1:
                    debug_print("More then 1 datafile id provided for editing, editing first : {}".format(ids[0]))
                return HttpResponseRedirect(reverse("datafile_edit", kwargs={"pk":ids[0]}))
        if "datafile_delete" in request.POST:
            print("DELETING FILES")
            ids=get_checked_datafiles(request.POST)
            delete_datafiles(ids, request.user)
        return HttpResponseRedirect(reverse("profile"))
    def get(self, request):
        print("ProfileView get: {}".format(request))
        return super().get(request)
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        print("in ProfileView : ")
        print( context)
        # user created problems
        context["problems"]=ProblemModel.objects.filter(author=self.request.user)
        context["codes"]=CodeModel.objects.filter(author=self.request.user)
        context["files"]=DataFileModel.objects.filter(author=self.request.user)
        
        # permissions
        context["code_add_permission"]=(self.request.user.is_superuser or \
                                        self.request.user.is_authenticated)
        context["code_edit_permission"]=(self.request.user.is_superuser or \
                                        self.request.user.is_authenticated)
        context["code_delete_permission"]=(self.request.user.is_superuser or \
                                        self.request.user.is_authenticated)
        context["datafile_add_permission"]=(self.request.user.is_superuser or \
                                        self.request.user.is_authenticated)
        context["datafile_edit_permission"]=(self.request.user.is_superuser or \
                                        self.request.user.is_authenticated)
        context["datafile_delete_permission"]=(self.request.user.is_superuser or \
                                        self.request.user.is_authenticated)
        return context


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

