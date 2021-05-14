from django.urls import path

from .views import DetailView, AddView, EditView

urlpatterns = [
        path("<int:pk>/", DetailView.as_view(), name="solver_detail"),
        path("<int:problem_id>/add/", AddView.as_view(), name="solver_add"),
        path("<int:pk>/edit/", EditView.as_view(), name="solver_edit"),
        ]
