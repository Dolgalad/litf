from django.urls import path

# import views
from .views import IndexView, DetailView, AddView, EditView, DataAddView, PostprocessAddView, PostprocessEditView
urlpatterns = [
        path("index/", IndexView.as_view(), name="problem_index"),
        path("add/", AddView.as_view(), name="problem_add"),
        path("<int:pk>/", DetailView.as_view(), name="problem_detail"),
        path("edit/<int:pk>/", EditView.as_view(), name="problem_edit"),
        path("<int:pk>/data_add", DataAddView.as_view(), name="problem_datafile_add"),

        path("<int:pk>/postprocess_add", PostprocessAddView.as_view(), name="postprocess_add"),
        path("postprocess_edit/<int:pk>/", PostprocessEditView.as_view(), name="postprocess_edit"),
        
        ]
