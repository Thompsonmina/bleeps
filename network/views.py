from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Post, Like

LOGIN_URL = "/login"

def index(request):
    return render(request, "network/index.html")

def home(request):
    return render(request, "network/index.html")

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
            print("got here fam")
            post.author = request.user
            post.save()
        except:
            # send error message to client 
             return JsonResponse({"success":False, "error":form.errors})

        return JsonResponse({"success":True})

def edit_profile(request):
    return render(request, "network/edit_profile.html")

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

