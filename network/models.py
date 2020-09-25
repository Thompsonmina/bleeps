from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
	bio = models.CharField(max_length=200, blank=True)
	following = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="followers")
	
	def likePost(self, post):
		Like.objects.create(user=self, post=post)

	def unlikePost(self, post):
		Like.objects.filter(post=post, user=self).delete()

	def follow(self, *person):
		self.following.add(*person)

	def unfollow(self, *person):
		self.following.remove(*person)

class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
	content = models.CharField(max_length=300)
	timestamp = models.DateTimeField(auto_now_add=True)
	edited = models.BooleanField(default=False)

	def editPost(self, newcontent):
		self.content = newcontent
		self.save()

	def totalLikes(self):
		return self.likes.count()

	def __str__(self):
		return f"{self.author} posted"


class Like(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

	class Meta:
		constraints = [models.UniqueConstraint(fields=["user", "post"], name="unique_likes_per_user")]

	def __str__(self):
		return f"{self.user} liked"