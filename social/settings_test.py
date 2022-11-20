from .settings_base import *  # noqa: F401,F403

DEBUG: bool = True

SECRET_KEY: str = "test_secret_key"

CSRF_COOKIE_SECURE: bool = False
SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = False
SECURE_HSTS_PRELOAD: bool = False
SECURE_SSL_REDIRECT: bool = False
SESSION_COOKIE_SECURE: bool = False
SECURE_BROWSER_XSS_FILTER: bool = False

SECURE_HSTS_SECONDS: int = 0

ADMIN_URL_PREPEND: str = "prepend"

DATABASES: dict = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}
