from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class GenericViewTests(TestCase):
    def test_DashboardView(self):
        url = reverse("dwitter:dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Dwitter", response.content.decode("utf-8"))


class ProfileViewTests(TestCase):
    def setUp(self):
        self.test_username = "test_username"

    def test_ProfileListView_unauthenticated(self):
        url = reverse("dwitter:profile_list")
        print(url)
        response = self.client.get(url, follow=True)

        # verify we get a 200 OK but that the username is not listed
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.test_username, response.content.decode("utf-8"))

        # Create the user
        User.objects.create(username=self.test_username)
        response = self.client.get(url)

        # should still get a 200 OK and now have the user listed
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.test_username, response.content.decode("utf-8"))

    def test_ProfileListView_authenticated(self):
        """
        There was a slight modification to how we handle authenticated vs unauthenticated rendering of this view
        Namely, self.request.user = AnonymousUser when unauthenticated so we had to patch it to not try to filter by
        AnonymousUser when running get_queryset().
        """
        url = reverse("dwitter:profile_list")

        user = User.objects.create(username=self.test_username)
        self.client.force_login(user)

        response = self.client.get(url)

        # should still get a 200 OK but profile_list does not display the logged in users dwitter handle
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.test_username, response.content.decode("utf-8"))

    def test_ProfileDetailView(self):
        username = "test_username"

        url = reverse("dwitter:profile", args=[username])
        response = self.client.get(url)

        # verify we get a 404 Not Found but that the username is not listed
        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.content.decode("utf-8").lower())

        # Create the user
        User.objects.create(username=username)
        response = self.client.get(url)

        # should still get a 200 OK and now have the user listed
        self.assertEqual(response.status_code, 200)
        self.assertIn(username, response.content.decode("utf-8"))
