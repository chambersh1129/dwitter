from django.contrib.auth.models import User
from django.test import TestCase

from dwitter.models import Dweet, Profile


class DweetModelTests(TestCase):
    def setUp(self):
        self.test_username = "test_username"
        self.test_dweet = "this is a test dweet"

    def test_dweet_creation(self):
        # verify there are currently no users or profiles in case fixtures are introduced in the future
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)

        # create a user and verify 1 user and 1 profile exists
        user = User.objects.create(username=self.test_username)
        self.assertEqual(User.objects.count(), 1)

        # create a dweet, make sure it is correcly linked to the user
        dweet = Dweet.objects.create(user=user, body=self.test_dweet)
        self.assertEqual(Dweet.objects.count(), 1)
        self.assertEqual(user.dweets.count(), 1)

        self.assertEqual(dweet.body, self.test_dweet)
        self.assertEqual(user.dweets.first().body, self.test_dweet)
        self.assertIn(self.test_username, str(dweet))


class ProfileModelTests(TestCase):
    def setUp(self):
        self.test_username = "test_username"

    def test_profile_creation(self):
        # verify there are currently no users or profiles in case fixtures are introduced in the future
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)

        # create a user and verify 1 user and 1 profile exists
        user = User.objects.create(username=self.test_username)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

        # verify both user and profile are named correctly/string methods work
        profile = Profile.objects.get(user=user)
        self.assertEqual(user.username, self.test_username)
        self.assertEqual(str(profile), self.test_username)

        # verify the user follows themselves as part of the post_save action
        self.assertTrue(profile in user.profile.followed_by.all())
        self.assertTrue(profile in user.profile.follows.all())
