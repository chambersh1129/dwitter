from django.contrib.auth.models import User
from django.test import TestCase

from dwitter.models import Profile


class ProfileModelTests(TestCase):
    def test_profile_creation(self):
        # verify there are currently no users or profiles in case fixtures are introduced in the future
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)

        # create a user and verify 1 user and 1 profile exists
        username = "test_username"
        user = User.objects.create(username=username)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)

        # verify both user and profile are named correctly/string methods work
        profile = Profile.objects.get(user=user)
        self.assertEqual(user.username, username)
        self.assertEqual(str(profile), username)

        # verify the user follows themselves as part of the post_save action
        self.assertTrue(profile in user.profile.followed_by.all())
        self.assertTrue(profile in user.profile.follows.all())
