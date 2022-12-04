"""Dwitter admin.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/ref/contrib/admin/

Unregister the default User admin page and overwrite it with a ModelAdmin page
that includes the Profile model fields
"""
from typing import Type

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Model

from .models import Dweet, Profile

User = get_user_model()

admin.site.unregister(User)
admin.site.register(Dweet)


class ProfileInLine(admin.StackedInline):
    """Add profile fields to User table in django admin.

    Args:
        admin (StackedInLine): List profile fields as if they were User fields

    """

    model: Type[Model] = Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Overwrite the default User admin to add ProfileInLine.

    Args:
        admin (ModelAdmin): ModelAdmin for the User model

    """

    fields: list = ["username"]
    inlines: list = [ProfileInLine]
