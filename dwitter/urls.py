"""Urls for the "dwitter" application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path

from .views import DweetListView, HomeView, ProfileListView

app_name = "dwitter"

urlpatterns: list = [
    path("", HomeView.as_view(), name="home"),
    path("dweet/list", DweetListView.as_view(), name="dweet-list"),
    path("profile/list", ProfileListView.as_view(), name="profile-list"),
]
