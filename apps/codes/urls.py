from django.urls import path
from django.views.generic import ListView

from .views import AddView, DetailView, EditView
from .views import DataAddView, DataEditView, DataDetailView
# my models
from .models import CodeModel

# output download view
from .views import output_download_view, stderr_download_view, stdout_download_view

class CodeListView(ListView):
    model=CodeModel

urlpatterns = [
        path("index/", CodeListView.as_view()),
        path("add/", AddView.as_view(),name="code_add"),
        path("<int:pk>/", DetailView.as_view(), name="code_detail"),
        path("edit/<int:pk>/", EditView.as_view(), name="code_edit"),
        # data files
        path("data_add", DataAddView.as_view(), name="datafile_add"),
        path("<int:pk>/data_add", DataAddView.as_view(), name="code_datafile_add"),
        path("data_edit/<int:pk>/", DataEditView.as_view(), name="datafile_edit"),
        path("data/<int:pk>/", DataDetailView.as_view(), name="datafile_detail"),

        # result download
        path("output/<int:exe_id>/", output_download_view, name="output_download"),
        path("stderr/<int:exe_id>/", stderr_download_view, name="stderr_download"),
        path("stdout/<int:exe_id>/", stdout_download_view, name="stdout_download"),
        ]
