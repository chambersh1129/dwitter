# dwitter/urls.py

from django.urls import path

from .views import Dashboard, ProfileDetail, ProfileList

app_name = "dwitter"

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("profile_list/", ProfileList.as_view(), name="profile_list"),
    path("profile/<str:username>", ProfileDetail.as_view(), name="profile"),
]
