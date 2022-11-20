import environ
from django.core.management.utils import get_random_secret_key
from django.utils.crypto import get_random_string

from .settings_base import *  # noqa: F403

env = environ.Env()

# Load environmental variables
environ.Env.read_env(BASE_DIR / ".env")  # noqa: F405

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = env("DJANGO_SECRET_KEY", default=get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = env.bool("DJANGO_DEBUG", default=False)

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES: dict = {"default": env.db_url("DATABASE_URL", default="sqlite:///db.sqlite3")}

# Security Settings
ADMIN_URL_PREPEND: str = env.str("DJANGO_ADMIN_URL_PREPEND", default=get_random_string())
CSRF_COOKIE_SECURE: bool = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
SECURE_BROWSER_XSS_FILTER: bool = env.bool("DJANGO_SECURE_BROWSER_XSS_FILTER", default=True)
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD: bool = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_HSTS_SECONDS: int = env.int("DJANGO_SECURE_HSTS_SECONDS", default=2592000)
SECURE_PROXY_SSL_HEADER: str = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT: bool = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE: bool = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
