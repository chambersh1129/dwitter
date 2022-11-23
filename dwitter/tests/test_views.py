from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from dwitter.models import Dweet


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.user_1_dweet = Dweet.objects.create(user=self.user_1, body="this is a dweet by user_1")
        self.user_2 = User.objects.create(username="user_2")
        self.user_2_dweet = Dweet.objects.create(user=self.user_2, body="this is a dweet by user_2")

    def test_DashboardView_dweets_unauthenticated(self):
        """
        Unauthenticated requests should see all dweets
        """
        url = reverse("dwitter:dashboard")

        # should still get a 200 OK and see both users and both dweets
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertIn(self.user_1_dweet.body, response.content.decode("utf-8"))
        self.assertIn(self.user_2.username, response.content.decode("utf-8"))
        self.assertIn(self.user_2_dweet.body, response.content.decode("utf-8"))

        # delete the dweets and test again
        # should get 200 OK but dweets/users no longer show up
        Dweet.objects.all().delete()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertNotIn(self.user_1_dweet.body, response.content.decode("utf-8"))
        self.assertNotIn(self.user_2.username, response.content.decode("utf-8"))
        self.assertNotIn(self.user_2_dweet.body, response.content.decode("utf-8"))

    def test_DashboardView_dweets_authenticated(self):
        """
        Authenticated requests should only see dweets by who they are following
        """
        url = reverse("dwitter:dashboard")

        # log the user in
        self.client.force_login(self.user_1)

        # dashboard should not show any dweets because user_1 does not follow anyone
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertNotIn(self.user_1_dweet.body, response.content.decode("utf-8"))
        self.assertNotIn(self.user_2.username, response.content.decode("utf-8"))
        self.assertNotIn(self.user_2_dweet.body, response.content.decode("utf-8"))

        # have user_1 follow user_2
        self.user_1.profile.follows.add(self.user_2.profile)

        # dashboard should show user_2 dweet but not user_1
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertNotIn(self.user_1_dweet.body, response.content.decode("utf-8"))
        self.assertIn(self.user_2.username, response.content.decode("utf-8"))
        self.assertIn(self.user_2_dweet.body, response.content.decode("utf-8"))


class ProfileDetailViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.user_1_dweet = Dweet.objects.create(user=self.user_1, body="this is a dweet by user_1")
        self.user_2 = User.objects.create(username="user_2")
        self.user_2_dweet = Dweet.objects.create(user=self.user_2, body="this is a dweet by user_2")

    def test_ProfileDetailView(self):
        """
        Profile should show the user and all of their tweets
        """
        url = reverse("dwitter:profile", args=[self.user_1.username])

        # should get a 200 OK and list the user
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertIn(self.user_1_dweet.body, response.content.decode("utf-8"))

        # try again with a username that does not exist, should get a 404
        # TODO create a catch-all 404 page
        url = reverse("dwitter:profile", args=["not_a_user"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_ProfileDetailView_post_unauthenticated(self):
        """
        Anonymous user cannot follow/unfollow a user.  Buttons should not render in HTML template if user is not
        authenticated but this is an extra precaution
        """
        url = reverse("dwitter:profile", args=[self.user_1.username])

        # build the payload to follow
        data = {"follow": "follow"}

        # should get a 200 OK but no change in follows/followed_by
        # users automatically follow themselves, so user_1 should only have itself in the follows/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.user_1.profile.follows.all()), 1)
        self.assertEqual(len(self.user_1.profile.followed_by.all()), 1)

    def test_ProfileDetailView_post_other_user(self):
        """
        Submitting the form should add/remove the profile to the list of users the requester follows
        """
        url = reverse("dwitter:profile", args=[self.user_1.username])

        # login user_2 so they can follow user_1
        self.client.force_login(self.user_2)

        # build the payload to follow
        data = {"follow": "follow"}

        # make sure user_2 does not currently follow user_1
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # should get a 200 OK and user_2 is now following user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # making the exact same call doesn't blow up and user_2 still follows user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # build the payload to unfollow
        data = {"follow": "unfollow"}

        # should get a 200 OK and user_2 is no longer following user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # making the exact same call doesn't blow up and user_2 still not following user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

    def test_ProfileDetailView_post_self(self):
        """
        A User should not be able to follow/unfollow themselves
        """
        url = reverse("dwitter:profile", args=[self.user_1.username])

        # login user_2 so they can follow user_1
        self.client.force_login(self.user_1)

        # build the payload to follow
        data = {"follow": "follow"}

        # user_1 should already be following user_1
        self.assertIn(self.user_1.profile, self.user_1.profile.follows.all())

        # should get a 200 OK and no change in follows/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.profile, self.user_1.profile.follows.all())

        # build the payload to follow
        data = {"follow": "follow"}

        # should get a 200 OK and no change in follows/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.profile, self.user_1.profile.follows.all())

    def test_ProfileDetailView_post_bad_payload(self):
        """
        If value for "follow" is anything other than follow/unfollow, nothing should happen
        """
        url = reverse("dwitter:profile", args=[self.user_1.username])

        # login user_2
        self.client.force_login(self.user_2)

        # build the payload to follow
        data = {"follow": "tacos"}

        # should get a 200 OK and there should be no change in follow/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # second test with an unsupported key
        data = {"tacos": "follow"}

        # should get a 200 OK and there should be no change in follow/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())


class ProfileListViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.user_1_dweet = Dweet.objects.create(user=self.user_1, body="this is a dweet by user_1")
        self.user_2 = User.objects.create(username="user_2")
        self.user_2_dweet = Dweet.objects.create(user=self.user_2, body="this is a dweet by user_2")

    def test_ProfileListView_unauthenticated(self):
        """
        Unauthenticated requests should see all users
        """
        url = reverse("dwitter:profile-list")

        # Should get a 200 OK and see both users
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertIn(self.user_2.username, response.content.decode("utf-8"))

    def test_ProfileListView_authenticated(self):
        """
        Authenticated requests should all users except themselves
        """
        url = reverse("dwitter:profile-list")

        # log in user_1
        self.client.force_login(self.user_1)

        # Should get a 200 OK and should see only user_2
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.username, response.content.decode("utf-8"))
        self.assertIn(self.user_2.username, response.content.decode("utf-8"))
