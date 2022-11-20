# dwitter/urls.py

from django.urls import re_path

from .views import dashboard

app_name = "dwitter"

urlpatterns = [
    re_path(r"", dashboard.as_view(), name="dashboard"),
]
