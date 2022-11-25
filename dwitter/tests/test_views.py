from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dwitter.models import Dweet

User = get_user_model()


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
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_1_dweet.body, content)
        self.assertIn(self.user_2.username, content)
        self.assertIn(self.user_2_dweet.body, content)

        # delete the dweets and test again
        # should get 200 OK but dweets/users no longer show up
        Dweet.objects.all().delete()

        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user_1.username, content)
        self.assertNotIn(self.user_1_dweet.body, content)
        self.assertNotIn(self.user_2.username, content)
        self.assertNotIn(self.user_2_dweet.body, content)

    def test_DashboardView_dweets_authenticated(self):
        """
        Authenticated requests should only see dweets by who they are following
        """
        url = reverse("dwitter:dashboard")

        # log the user in
        self.client.force_login(self.user_1)

        # dashboard should only see their own dweets
        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_1_dweet.body, content)
        self.assertNotIn(self.user_2.username, content)
        self.assertNotIn(self.user_2_dweet.body, content)

        # have user_1 follow user_2
        self.user_1.profile.follows.add(self.user_2.profile)

        # dashboard should show user_2 dweets
        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_1_dweet.body, content)
        self.assertIn(self.user_2.username, content)
        self.assertIn(self.user_2_dweet.body, content)


class DweetCreateViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.dweet_body = "This is a test dweet"

    def test_DweetCreateView_GET(self):
        """
        GET not allowed and should redirect to /
        """
        url = reverse("dwitter:dweet-create")

        pre_dweet_count = Dweet.objects.count()

        # should redirect to homepage
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertEqual(Dweet.objects.count(), pre_dweet_count)

    def test_DweetCreateView_POST_unauthenticated(self):
        """
        Must be authenticated to dweet so should just redirect
        """
        url = reverse("dwitter:dweet-create")

        # build the payload to follow
        data = {"body": self.dweet_body}

        pre_dweet_count = Dweet.objects.count()

        # should get 403 Bad Request but no change in follows/followed_by
        # Dweet should not be created, count should be the same
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Dweet.objects.count(), pre_dweet_count)

    def test_DweetCreateView_POST_authenticated(self):
        """
        Should create a new Dweet for user_1
        """
        url = reverse("dwitter:dweet-create")
        redirect_url = reverse("dwitter:dashboard")

        # login user_1
        self.client.force_login(self.user_1)

        # build the payload to follow
        data = {"body": self.dweet_body}

        pre_dweet_count = Dweet.objects.filter(user=self.user_1).count()

        # should redirect to homepage
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)
        self.assertEqual(Dweet.objects.filter(user=self.user_1).count(), pre_dweet_count + 1)

    def test_DweetCreateView_POST_bad_data(self):
        """
        Should not create a new Dweet for user_1
        """
        url = reverse("dwitter:dweet-create")
        redirect_url = reverse("dwitter:dashboard")

        # login user_1
        self.client.force_login(self.user_1)

        # build the payload to follow
        data = {"taco": self.dweet_body}

        pre_dweet_count = Dweet.objects.filter(user=self.user_1).count()

        # should redirect to homepage
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)
        self.assertEqual(Dweet.objects.filter(user=self.user_1).count(), pre_dweet_count)

        # test dweet too long
        data = {"dweet": "a" * (Dweet.body.field.max_length + 1)}

        # should redirect to homepage
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirect_url)
        self.assertEqual(Dweet.objects.filter(user=self.user_1).count(), pre_dweet_count)


class ProfileDetailViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.user_1_dweet = Dweet.objects.create(user=self.user_1, body="this is a dweet by user_1")
        self.user_2 = User.objects.create(username="user_2")
        self.user_2_dweet = Dweet.objects.create(user=self.user_2, body="this is a dweet by user_2")

    def test_ProfileDetailView_unauthenticated(self):
        """
        Profile should show the user and all of their tweets
        """
        url = reverse("dwitter:profile-detail", args=[self.user_1.username])

        # should get a 200 OK and list the user
        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_1_dweet.body, content)

        # try again with a username that does not exist, should get a 404
        # TODO create a catch-all 404 page
        url = reverse("dwitter:profile-detail", args=["not_a_user"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_ProfileDetailView_authenticated(self):
        """
        When rendering your own profile the dweet form should be displayed along with any dweets
        """
        url = reverse("dwitter:profile-detail", args=[self.user_1.username])

        # login user_1
        self.client.force_login(self.user_1)

        # The form should have a textarea named "body" to coincide with the Dweet model
        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn('<textarea name="body"', content)

        # user_1's username and dweets should also be shown, but not user_2's
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_1_dweet.body, content)
        self.assertNotIn(self.user_2.username, content)
        self.assertNotIn(self.user_2_dweet.body, content)


class ProfileFollowViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.user_2 = User.objects.create(username="user_2")

    def test_ProfileFollowView_GET(self):
        """
        GET not allowed and should redirect to the profile of the user you attempted to follow
        """
        url = reverse("dwitter:profile-follow", args=[self.user_1.username])
        redirect_url = reverse("dwitter:profile-detail", args=[self.user_1.username])

        # redirect to user_1's profile with no change in follows/followed_by count
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(redirect_url, response.url)
        self.assertEqual(len(self.user_1.profile.follows.all()), 1)
        self.assertEqual(len(self.user_1.profile.followed_by.all()), 1)

    def test_ProfileFollowView_POST_unauthenticated(self):
        """
        Anonymous user cannot follow/unfollow a user
        """
        url = reverse("dwitter:profile-follow", args=[self.user_1.username])

        # build the payload to follow
        data = {"follow": "follow"}

        # should get 403 Bad Request but no change in follows/followed_by
        # users automatically follow themselves, so user_1 should only have itself in the follows/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(self.user_1.profile.follows.all()), 1)
        self.assertEqual(len(self.user_1.profile.followed_by.all()), 1)

    def test_ProfileFollowView_POST_other_user(self):
        """
        Submitting the form should add/remove the profile to the list of users the requester follows
        """
        url = reverse("dwitter:profile-follow", args=[self.user_1.username])
        redirect_url = reverse("dwitter:profile-detail", args=[self.user_1.username])

        # login user_2 so they can follow user_1
        self.client.force_login(self.user_2)

        # build the payload to follow
        data = {"follow": "follow"}

        # make sure user_2 does not currently follow user_1
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # should get a redirect and user_2 is now following user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(redirect_url, response.url)
        self.assertIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # making the exact same call doesn't blow up and user_2 still follows user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(redirect_url, response.url)
        self.assertIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # build the payload to unfollow
        data = {"follow": "unfollow"}

        # should get a redirect and user_2 is no longer following user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(redirect_url, response.url)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # making the exact same call doesn't blow up and user_2 still not following user_1
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(redirect_url, response.url)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

    def test_ProfileFollowView_POST_self(self):
        """
        A User should not be able to follow/unfollow themselves
        """
        url = reverse("dwitter:profile-follow", args=[self.user_1.username])

        # login user_2 so they can follow user_1
        self.client.force_login(self.user_1)

        # build the payload to follow
        data = {"follow": "follow"}

        # user_1 should already be following user_1
        self.assertIn(self.user_1.profile, self.user_1.profile.follows.all())

        # should get a redirect and no change in follows/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user_1.profile, self.user_1.profile.follows.all())

        # build the payload to follow
        data = {"follow": "follow"}

        # should get a redirect and no change in follows/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user_1.profile, self.user_1.profile.follows.all())

    def test_ProfileFollowView_POST_bad_payload(self):
        """
        If value for "follow" is anything other than follow/unfollow, nothing should happen
        """
        url = reverse("dwitter:profile-follow", args=[self.user_1.username])

        # login user_2
        self.client.force_login(self.user_2)

        # build the payload to follow
        data = {"follow": "tacos"}

        # should get a 200 OK and there should be no change in follow/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())

        # second test with an unsupported key
        data = {"tacos": "follow"}

        # should get a 200 OK and there should be no change in follow/followed_by
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(self.user_1.profile, self.user_2.profile.follows.all())
        self.assertNotIn(self.user_2.profile, self.user_1.profile.followed_by.all())


class ProfileListViewTests(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username="user_1")
        self.user_2 = User.objects.create(username="user_2")

    def test_ProfileListView_unauthenticated(self):
        """
        Unauthenticated requests should see all users
        """
        url = reverse("dwitter:profile-list")

        # Should get a 200 OK and see both users
        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_2.username, content)

    def test_ProfileListView_authenticated(self):
        """
        Authenticated requests also should all users
        """
        url = reverse("dwitter:profile-list")

        # log in user_1
        self.client.force_login(self.user_1)

        # Should get a 200 OK and should see only user_2
        response = self.client.get(url)
        content = response.content.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_1.username, content)
        self.assertIn(self.user_2.username, content)
