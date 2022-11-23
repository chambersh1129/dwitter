from typing import Type

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Model

from .models import Dweet, Profile

admin.site.unregister(User)
admin.site.register(Dweet)


class ProfileInLine(admin.StackedInline):
    model: Type[Model] = Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields: list = ["username"]
    inlines: list = [ProfileInLine]
