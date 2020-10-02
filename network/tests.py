from django.test import TestCase
from django.urls import reverse
from django.db.models import Count
from django.db.utils import IntegrityError

from .models import Like, Post, User
class ModelTests(TestCase):

	@classmethod
	def setUpClass(cls):
		""" populate test db with some dummmy values"""
		super().setUpClass()
		cls.ada = User.objects.create_user(username="ada", password="mynameisada")
		cls.paul = User.objects.create_user(username="paul", password="mynameispaul")
		cls.hannah = User.objects.create_user(username="hannah", password="hannahpassword")
		cls.obinna = User.objects.create_user(username="obinna", password="password")

		cls.post1 = Post.objects.create(author=cls.ada, content="creating content")
		cls.post2 = Post.objects.create(author=cls.obinna, content="loading")

		cls.adalikedpost2 = Like.objects.create(user=cls.ada, post=cls.post2)

	def test_user_object_created_successfully(self):
		""" test that a user instannce was created well in the db"""
		self.assertIsInstance(self.ada, User)
		self.assertEqual("ada", User.objects.get(id=1).username)

	def test_user_follow_method(self):
		""" test that the follow method works as expected """
		self.ada.follow(self.paul, self.hannah, self.obinna)
		following = self.ada.following.all()

		self.assertEqual(3, len(following))
		self.assertIn(self.paul, following)

	def test_user_unfollow_method(self):
		""" test that the unfollow method works as expected"""
		self.ada.follow(self.paul, self.hannah)
		self.ada.unfollow(self.paul)

		self.assertNotIn(self.paul, self.ada.following.all())

	def test_user_followers(self):
		"""  test that the many to many relationship is indeed asymmetrical on the model
		i.e following relationship is completely one sided"""
		self.hannah.follow(self.ada)
		self.obinna.follow(self.ada)
		self.paul.follow(self.ada)

		self.assertEqual(self.ada.followers.count(), 3)
		self.assertEqual(self.ada.following.count(), 0)

	def test_user_isFollowing_method(self):
		""" test that the isfollowing return true if following and false if not"""
		self.ada.follow(self.hannah)
		self.ada.follow(self.obinna)

		self.assertTrue(self.ada.isFollowing(self.hannah.id))
		self.assertTrue(self.ada.isFollowing(self.obinna.id))

		self.assertFalse(self.ada.isFollowing(self.paul.id))

	def test_user_likePost_method(self):
		""" test that the like post method actually works as intended"""
		self.hannah.likePost(self.post1)

		self.assertEqual(self.hannah, Like.objects.get(post=self.post1, user=self.hannah).user)

	def test_user_unlikePost_method(self):
		""" test that the unlike post method actually works """
		Like.objects.create(user=self.paul, post=self.post1)
		self.paul.unlikePost(self.post1)

		self.assertEqual(0, Like.objects.filter(user=self.paul, post=self.post1).count())

	def test_like_object_created_successfully(self):
		self.assertIsInstance(self.adalikedpost2, Like)

	def test_like_backrefs_on_user_and_post(self):
		self.assertEqual(self.adalikedpost2, self.ada.likes.get(pk=1))
		self.assertEqual(self.adalikedpost2, self.post2.likes.get(pk=1))

	def test_post_objects_created_successfully(self):
		self.assertIsInstance(self.post1, Post)

	def test_totalLikes_method(self):
		Like.objects.create(user=self.ada, post=self.post1)
		Like.objects.create(user=self.hannah, post=self.post1)
		Like.objects.create(user=self.paul, post=self.post1)

		self.assertEqual(3, self.post1.totalLikes())

	def test_that_a_post_cannot_be_liked_twice_by_the_same_user(self):
		with self.assertRaises(IntegrityError):
			Like.objects.create(user=self.ada, post=self.post1)
			Like.objects.create(user=self.ada, post=self.post1)
	
	def test_editPost_method(self):
		og_post = self.post1.content
		self.post1.editPost("this is a totally new message not the same")
		self.assertNotEqual(self.post1.content, og_post)
	
class ViewTests(TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.user = User.objects.create_user(username="ada", password="mynameisada")

	def test_create_post_route_post_succefully_created(self):
		self.client.force_login(self.user)
		data = {"content": "this is a message"}
		response = self.client.post(reverse("create_post"), data=data)

		self.assertEqual(1, Post.objects.count())
		self.assertJSONEqual(str(response.content, encoding="utf8"),
				 {"success":True})

	def test_create_post_route_handles_invalid_post(self):
		""" ensure that an error message is sent and a post is not created if the post fails its constraints"""
		self.client.force_login(self.user)
		content = "a word" * 300 # passes the 300 char limit
		data = {"content": content}
		response = self.client.post(reverse("create_post"), data=data)

		self.assertEqual(0, Post.objects.count())
		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_create_post_route_redirects_if_user_not_loggedIn(self):
		""" make sure an anon user doesnt have access to route"""
		content = "i am an anon user attempting to pass"
		data = {"content": content}
		response = self.client.post(reverse("create_post"), data=data)

		self.assertRedirects(response, f"/login?next={reverse('create_post')}")

	def test_edit_post_route_post_succefully_edited(self):
		self.client.force_login(self.user)
		""" ensure that a post has been updated with new content"""
		post = Post.objects.create(author=self.user, content="i will be edited")
		newcontent = "i come to replace"
		data = {"content": newcontent}
		response = self.client.post(reverse("edit_post", args=[post.id]), data=data)

		# querying for the same post because the it should have been updated 
		self.assertEqual(Post.objects.get(id=post.id).content, newcontent)
		self.assertTrue(Post.objects.get(id=post.id).edited)
		self.assertJSONEqual(str(response.content, encoding="utf8"),
				 {"success":True})

	def test_edit_post_route_handles_invalid_postID(self):
		""" ensure that the route handles a invalid post id arg in the url"""
		self.client.force_login(self.user)
		response = self.client.post(reverse("edit_post", args=[1]), data={"content": "blah blah"})

		# should fail because there isnt any post object at all
		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_edit_post_route_handles_invalid_post_content(self):
		self.client.force_login(self.user)
		post = Post.objects.create(author=self.user, content="i will be edited")
		newcontent = "i come to replace" * 300
		data = {"content": newcontent}
		response = self.client.post(reverse("edit_post", args=[post.id]), data=data)

		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_edit_post_route_redirects_if_user_not_loggedIn(self):
		""" make sure an anon user doesnt have access to route"""
		post = Post.objects.create(author=self.user, content="i will be edited")		
		content = "i am an anon user attempting to pass"
		data = {"content": content}
		response = self.client.post(reverse("edit_post", args=[post.id]), data=data)

		self.assertRedirects(response, f"/login?next={reverse('edit_post', args=[post.id])}")

	def test_edit_post_route_unauthorized_User(self):
		""" ensure that only the owner of a post can edit it"""
		self.client.force_login(self.user)
		another_user = User.objects.create_user(username="prince", password="password")
		
		post = Post.objects.create(author=another_user, content="i will be edited")		
		data = {"content":"content"}
		response = self.client.post(reverse("edit_post", args=[post.id]), data=data)

		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_show_all_posts_route_works_well(self):
		""" ensure that the route does as advertised"""

		# create some posts
		Post.objects.create(author=self.user, content="post 1")		
		Post.objects.create(author=self.user, content="post 2")		

		response = self.client.get(reverse("show_all"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("posts", response.context)
		self.assertTemplateUsed(response, template_name="network/display_chats.html")	

	def test_feeds_route_works_well(self):
		""" ensure that the route only shows the posts of the users follwoing"""
		self.client.force_login(self.user)
		friend1 = User.objects.create_user(username="prince", password="password")
		friend2 = User.objects.create_user(username="damian", password="password")
		friend3 = User.objects.create_user(username="queen", password="password")
		
		self.user.follow(friend1, friend2, friend3)

		# create some posts
		Post.objects.create(author=friend3, content="post 1")		
		Post.objects.create(author=friend2, content="post 2")		
		Post.objects.create(author=friend1, content="post 2")		

		response = self.client.get(reverse("feed"))

		self.assertEqual(response.status_code, 200)
		self.assertTrue(all([post.author in [friend1, friend2, friend3] for post in response.context["posts"]]))
		self.assertTemplateUsed(response, template_name="network/display_chats.html")	

	def test_feeds_route_context_returns_empty_List_if_not_following(self):
		""" ensure that no post are displayed if the user is not folllowing any one"""
		self.client.force_login(self.user)
		another_user = User.objects.create_user(username="prince", password="password")

		# create some posts
		Post.objects.create(author=another_user, content="post 1")		
		Post.objects.create(author=self.user, content="post 2")		

		response = self.client.get(reverse("feed"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(0, len(response.context["posts"]))
		self.assertTemplateUsed(response, template_name="network/display_chats.html")	

	def test_feed_route_redirects_if_user_not_loggedIn(self):
		""" make sure an anon user doesnt have access to route"""
		response = self.client.get(reverse("feed"))
		self.assertRedirects(response, f"/login?next={reverse('feed')}")

	def test_profile_route_works_as_expected(self):
		""" ensure that the profile route works correctly """
		self.client.force_login(self.user)
		response = self.client.get(reverse("profile", args=[self.user.username]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(self.user, response.context["selected_user"])
		self.assertTrue(all([post.author == self.user for post in response.context["posts"]]))
		self.assertTemplateUsed(response, template_name="network/profile.html")	

	def test_profile_route_handles_invalid_url_argument(self):
		""" ensure that we get an error if a wrong username is put in the url"""
		self.client.force_login(self.user)
		response = self.client.get(reverse("profile", args=["wrong thing"]))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error", response.context)
		self.assertTemplateUsed(response, template_name="network/errors.html")

	def test_edit_profile_route_bio_succefully_edited(self):
		self.client.force_login(self.user)
		""" ensure that a user's bio has been updated with new content"""
		newbio = "living life"
		data = {"bio": newbio}
		response = self.client.post(reverse("edit_profile", args=[self.user.username]), data=data)

		# querying for the user because the it should have been updated 
		self.assertEqual(User.objects.get(username=self.user.username).bio, newbio)
		self.assertJSONEqual(str(response.content, encoding="utf8"),
				 {"success":True})

	def test_edit_profile_route_handles_invalid_username(self):
		""" ensure that the route handles a invalid post id arg in the url"""
		self.client.force_login(self.user)
		response = self.client.post(reverse("edit_profile", args=["random name"]), data={"content": "blah blah"})

		# should fail because there isnt any user with that name at all
		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_edit_profile_route_handles_invalid_post_content(self):
		self.client.force_login(self.user)
		
		newbio = "living life" * 100
		data = {"bio": newbio}
		response = self.client.post(reverse("edit_profile", args=[self.user.username]), data=data)

		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_edit_profile_route_redirects_if_user_not_loggedIn(self):
		""" make sure an anon user doesnt have access to route"""
		newbio = "living life"
		data = {"bio": newbio}
		response = self.client.post(reverse("edit_profile", args=[self.user.username]), data=data)

		self.assertRedirects(response, f"/login?next={reverse('edit_profile', args=[self.user.username])}")

	def test_edit_profile_route_unauthorized_User(self):
		""" ensure that only the user can edit it"""
		self.client.force_login(self.user)
		another_user = User.objects.create_user(username="prince", password="password")
		
		newbio = "living life"
		data = {"bio": newbio}		
		response = self.client.post(reverse("edit_profile", args=[another_user.username]), data=data)

		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_follow_route_works_as_expected(self):
		self.client.force_login(self.user)
		another_user = User.objects.create_user(username="prince", password="password")

		response = self.client.post(reverse("follow"), data={"otheruser_id":another_user.id})

		self.assertTrue(self.user.isFollowing(another_user.id))
		self.assertJSONEqual(str(response.content, encoding="utf8"),
				 {"success":True})

	def test_follow_route_handles_invalid_arguements(self):
		""" ensure that the route works can hanle wrong arguements"""
		self.client.force_login(self.user)
		response = self.client.post(reverse("follow"), data={"otheruser_id":
			"passing a string instead of a number"})

		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_follow_route_redirects_if_user_not_loggedIn(self):
		""" make sure an anon user doesnt have access to route"""
		response = self.client.post(reverse("follow"), data={"otheruser_id":3})
		self.assertRedirects(response, f"/login?next={reverse('follow')}")

	def test_unfollow_route_works_as_expected(self):
		self.client.force_login(self.user)
		another_user = User.objects.create_user(username="prince", password="password")
		self.user.follow(another_user)

		response = self.client.post(reverse("unfollow"), data={"otheruser_id":another_user.id})
		self.assertFalse(self.user.isFollowing(another_user.id))
		self.assertJSONEqual(str(response.content, encoding="utf8"),
				 {"success":True})

	def test_unfollow_route_handles_invalid_arguements(self):
		""" ensure that the route works can hanle wrong arguements"""
		self.client.force_login(self.user)
		response = self.client.post(reverse("unfollow"), data={"otheruser_id":
			"passing a string instead of a number"})

		self.assertIn("error", str(response.content, encoding="utf8"))

	def test_unfollow_route_redirects_if_user_not_loggedIn(self):
		""" make sure an anon user doesnt have access to route"""
		response = self.client.post(reverse("unfollow"), data={"otheruser_id":3})
		self.assertRedirects(response, f"/login?next={reverse('unfollow')}")

	def test_show_following_route_works_as_expected(self):
		self.client.force_login(self.user)
		friend1 = User.objects.create_user(username="prince", password="password")
		friend2 = User.objects.create_user(username="damian", password="password")
		friend3 = User.objects.create_user(username="queen", password="password")
		self.user.follow(friend3, friend2, friend1)

		response = self.client.get(reverse("show_following", args=[self.user.username]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(self.user, response.context["selected_user"])
		self.assertTrue(all([self.user.isFollowing(person.id) for person in response.context["following"]]))
		self.assertTemplateUsed(response, template_name="network/friends.html")	

	def test_show_following_route_invalid_url_argument(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("show_following", args=["wrong thing"]))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error", response.context)
		self.assertTemplateUsed(response, template_name="network/errors.html")

	def test_show_followers_route_works_as_expected(self):
		self.client.force_login(self.user)
		friend1 = User.objects.create_user(username="prince", password="password")
		friend2 = User.objects.create_user(username="damian", password="password")
		friend1.follow(self.user)
		friend2.follow(self.user)

		response = self.client.get(reverse("show_followers", args=[self.user.username]))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(self.user, response.context["selected_user"])
		self.assertTrue(all([person.isFollowing(self.user.id) for person in response.context["followers"]]))
		self.assertTemplateUsed(response, template_name="network/friends.html")	


	def test_show_followers_route_invalid_url_argument(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("show_followers", args=["wrong thing"]))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error", response.context)
		self.assertTemplateUsed(response, template_name="network/errors.html")

	