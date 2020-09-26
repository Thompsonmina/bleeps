
from django.urls import path

from . import views

urlpatterns = [
    path("", views.show_all_posts, name="show_all"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile", views.profile, name="profile"),
    path("friends", views.friends, name="friends"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("home", views.home, name="home"),
    path("create_post", views.create_post, name="create_post"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post")
]
