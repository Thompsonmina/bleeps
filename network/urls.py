
from django.urls import path

from . import views

urlpatterns = [
    path("", views.show_all_posts, name="show_all"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("edit_profile/<str:username>", views.edit_profile, name="edit_profile"),
	path("profile/<str:username>/following", views.show_following, name="show_following"),
	path("profile/<str:username>/followers", views.show_followers, name="show_followers"),
    path("feed", views.feed, name="feed"),
    path("create_post", views.create_post, name="create_post"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("like", views.like_post, name="like_post"),
    path("unlike", views.unlike_post, name="unlike_post")

]
