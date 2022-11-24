from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


# TODO when deleting a User we get a Foreign Key constraint if they have any Dweets
# figure out a work around, whether it is a soft delete of the user or simply setting the on_delete to CASCADE
class Dweet(models.Model):
    user = models.ForeignKey("auth.user", related_name="dweets", on_delete=models.DO_NOTHING)
    body = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: list = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user} {self.created_at:%Y-%m-%d %H:%M}: {self.body[:30]}..."


class Profile(models.Model):
    user = models.OneToOneField("auth.user", on_delete=models.CASCADE)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)

    class Meta:
        ordering: list = ["user__username"]

    def __str__(self) -> str:
        return self.user.username


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        user_profile.follows.add(user_profile)
