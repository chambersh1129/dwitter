# dwitter/urls.py

from django.urls import path

from .views import DashboardView, ProfileDetailView, ProfileListView

app_name = "dwitter"

urlpatterns: list = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("profile/<str:username>", ProfileDetailView.as_view(), name="profile"),
    path("profile_list/", ProfileListView.as_view(), name="profile_list"),
]
