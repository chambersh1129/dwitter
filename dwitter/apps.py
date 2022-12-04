"""Helps Django determine the "dwitter" application information.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/ref/applications/
"""
from django.apps import AppConfig


class DwitterConfig(AppConfig):
    """Dwitter application information.

    Args:
        AppConfig (AppConfig): Inherit from django.apps.AppConfig

    """

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "dwitter"
