from django.urls import path

# import views
from .views import LoginView, RegistrationView, ProfileView, logout_view

urlpatterns = [
        path("", LoginView.as_view()),
        #path("home/", HomeView.as_view()),
        path("login/", LoginView.as_view(), name="login"),
        path("logout/", logout_view, name="logout"),
        path("register/", RegistrationView.as_view(), name="register"),
        #path("thanks/", ThanksView.as_view()),
        path("profile", ProfileView.as_view(), name="profile"),
        #path("account/<int:user_id>/", AccountView.as_view()),
        ]
