from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Post, Like

LOGIN_URL = "/login"
PAGINATION_NUM = 10

def show_all_posts(request):
    """ get all the posts and display """
    posts = Post.objects.all().order_by("-timestamp")

    paginator = Paginator(posts, PAGINATION_NUM)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)
    return render(request, "network/display_chats.html", {"posts":posts, "isfeed":False})

@login_required(login_url=LOGIN_URL)
def feed(request):
    """ display only the posts of the people that a user is following"""
    # use preftch to efficienly get all the related data in 3 queries at once 
    user = User.objects.prefetch_related("followers__posts").get(id=request.user.id)
    follows = user.following.all()

    # if the user has people he/she is following
    if follows:
        # combine all the querysets and order in reverse chronological order and paginate
        posts = follows[0].posts.all().union(*[user.posts.all() for user in follows[1:]]).order_by("-timestamp")
        paginator = Paginator(posts, PAGINATION_NUM)
        page_number = request.GET.get("page")
        posts = paginator.get_page(page_number)
    else:
        posts = []

    return render(request, "network/display_chats.html", {"posts":posts, "isfeed":True})

def profile(request):
    return render(request, "network/profile.html")

def friends(request):
    return render(request, "network/friends.html")

@login_required(login_url=LOGIN_URL)
def create_post(request):
    if request.method == "POST":
        # create a model form for easy validation and saving of data
        postform = modelform_factory(Post, fields=["content"]) # using a modelform for easy validation and saving
        form = postform(request.POST)

        try:
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        except:
            # send error message to client 
             return JsonResponse({"success":False, "error":form.errors})

        return JsonResponse({"success":True})

@login_required(login_url=LOGIN_URL)
def edit_post(request, post_id):
    if request.method == "POST":
        try:
            # ensure that the post exists
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"success":False, "error":"post does not exist"})

        content = request.POST["content"]

        # modify the post
        if post.author == request.user:
            if 0 < len(content) <= 300:
                post.content = content
                post.edited = True
                post.save()
                return JsonResponse({"success":True})

            return JsonResponse({"success":False, "error":"content size is not within constraints"})

        else:
            return JsonResponse({"success":False, "error":"user doesnt have access"}, status=405)


def edit_profile(request):
    return render(request, "network/edit_profile.html")

@login_required(login_url=LOGIN_URL)
def follow(request):
    if request.method == "POST":
        # check if its a valid user
        try:
            try:
                int(request.POST["otheruser_id"])
            except:
                return JsonResponse({"success":False, "error":"data passed is not the appropiate type"})
            otheruser = User.objects.get(id=request.POST["otheruser_id"])
        except User.DoesNotExist:
            return JsonResponse({"success":False, "error":"no such user exists"})

        # start following person if not already following person
        if not request.user.isFollowing(otheruser.id):
            request.user.follow(otheruser)
        return JsonResponse({"success":True})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

