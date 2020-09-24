from django.contrib import admin

from .models import User, Like, Post
# Register your models here.

class UserAdmin(admin.ModelAdmin):
	filter_horizontal = ["following"]

admin.site.register(User, UserAdmin)

admin.site.register(Like)

admin.site.register(Post)