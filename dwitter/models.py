"""Forms for the "dwitter" application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/db/models/
"""
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


# TODO when deleting a User we get a Foreign Key constraint if they have any Dweets
# figure out a work around, whether it is a soft delete of the user or simply setting the on_delete to CASCADE
class Dweet(models.Model):
    """Dweet model to track what the user wrote and when."""

    user = models.ForeignKey("auth.user", related_name="dweets", on_delete=models.DO_NOTHING)  # type: ignore
    body = models.CharField(max_length=140)  # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)  # type: ignore

    class Meta:
        """Order the Dweets by reverse created at, aka newest at the top."""

        ordering: list = ["-created_at"]

    def __str__(self) -> str:
        """String magic method to provide a string representation of the model.

        Returns
            str: string representation of the model

        """
        return f"{self.user} {self.created_at:%Y-%m-%d %H:%M}: {self.body[:30]}..."


class Profile(models.Model):
    """Profile data to be combined/appended to the User model."""

    user = models.OneToOneField("auth.user", on_delete=models.CASCADE)  # type: ignore
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)  # type: ignore

    class Meta:
        """Order by alphabetical username."""

        ordering: list = ["user__username"]

    def __str__(self) -> str:
        """String magic method to provide a string representation of the model.

        Returns
            str: string representation of the model

        """
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(instance, created, **kwargs):
    """Post save method to automatically create the 1 to 1 relationship between the User model and a Profile model.

    Args:
        sender (User Model): Set to receive post_save signal from the User model
        instance (User Obj): Instance of the User model that was saved
        created (Boolean): Whether or not the model was just created

    """
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.add(user_profile)
