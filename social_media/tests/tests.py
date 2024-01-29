import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app import settings
from social_media.serializers import ProfileListSerializer
from social_media.models import Profile, Post

PROFILE_URL = reverse("social_media:profile-list")
POST_URL = reverse("social_media:post-list")
COMMENT_URL = reverse("social_media:comment-list")
LIKE_URL = reverse("social_media:comment-list")


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        url_list = [PROFILE_URL, POST_URL, COMMENT_URL, LIKE_URL]
        for url in url_list:
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="testfortest@test.com",
            password="Test122345",
            first_name="Test",
            last_name="Tester"
        )
        self.user2 = get_user_model().objects.create_user(
            email="testfor@test.com",
            password="Test122345",
            first_name="Joe",
            last_name="Doe"
        )
        self.profile1 = Profile.objects.create(owner=self.user, gender="Male")
        self.profile2 = Profile.objects.create(owner=self.user2, gender="Female")
        self.client.force_authenticate(self.user)

    def test_flter_profile_by_last_name(self):
        response = self.client.get(PROFILE_URL, {"last_name": "Doe"})

        serializer1 = ProfileListSerializer(self.profile1)
        serializer2 = ProfileListSerializer(self.profile2)

        self.assertNotIn(serializer1.data, response.data["results"])
        self.assertIn(serializer2.data, response.data["results"])

    def test_flter_profile_by_first_name(self):
        response = self.client.get(PROFILE_URL, {"first_name": "Test"})

        serializer1 = ProfileListSerializer(self.profile1)
        serializer2 = ProfileListSerializer(self.profile2)

        self.assertIn(serializer1.data, response.data["results"])
        self.assertNotIn(serializer2.data, response.data["results"])

    def test_upload_image(self):
        path = os.path.join("social_media", "tests", "test.jpg")
        image_data = {"image": open(path, "rb")}
        url = reverse("social_media:profile-upload-image", kwargs={"pk": self.profile1.id})
        response = self.client.post(url, image_data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["image"])

    def test_follow_action(self):
        url = reverse("social_media:profile-follow", kwargs={"pk": self.profile2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "You are now following this user.")
        self.assertTrue(self.user.profile.following.filter(id=self.profile2.id).exists())

    def test_follow_self_action(self):
        url = reverse("social_media:profile-follow", kwargs={"pk": self.profile1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You cannot follow yourself.")


    def test_follow_already_following_action(self):
        self.user.profile.following.add(self.profile2)
        url = reverse("social_media:profile-follow", kwargs={"pk": self.profile2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["detail"], "You are already following this user.")


    def test_unfollow_action(self):
        self.user.profile.following.add(self.profile2)
        url = reverse("social_media:profile-unfollow", kwargs={"pk": self.profile2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "You have unfollowed this user")
        # Перевірка, чи користувач вже не є фоловером profile2
        self.assertFalse(self.user.profile.following.filter(id=self.profile2.id).exists())
