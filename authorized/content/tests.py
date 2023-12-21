from django.test import TestCase
from .models import *


# Create your tests here.


class PostTest(TestCase):
    useremail = "temp@mail.com"
    postname = "postname"
    postcontent = "postcontent"

    def setUp(self):
        tempuser = User.objects.create(email=self.useremail)
        Post.manager.create(name=self.postname, content=self.postcontent, user=tempuser)

    def test_post_list(self):
        post = Post.objects.get(name=self.postname)
        response = self.client.get(f"/content/post/{post.pk}/")
        self.assertEqual(response.status_code, 200)
