from django.contrib import admin
from django.contrib.auth.models import User

from .models import Profile

admin.site.unregister(User)


class ProfileInLine(admin.StackedInline):
    model = Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ["username"]
    inlines = [ProfileInLine]
