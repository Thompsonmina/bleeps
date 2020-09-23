
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("friends", views.friends, name="friends"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("home", views.home, name="home")
]
