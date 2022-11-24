from typing import Type

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Model

from .models import Dweet, Profile

User = get_user_model()

admin.site.unregister(User)
admin.site.register(Dweet)


class ProfileInLine(admin.StackedInline):
    model: Type[Model] = Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields: list = ["username"]
    inlines: list = [ProfileInLine]
