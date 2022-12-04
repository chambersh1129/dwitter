"""Urls for the "dwitter" application.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path

from .views import DashboardView, DweetCreateView, ProfileDetailView, ProfileFollowView, ProfileListView

app_name = "dwitter"

urlpatterns: list = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("dweet/create/", DweetCreateView.as_view(), name="dweet-create"),
    path("profiles/<str:username>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/<str:username>/follow/", ProfileFollowView.as_view(), name="profile-follow"),
    path("profiles/", ProfileListView.as_view(), name="profile-list"),
]
