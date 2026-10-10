from django.conf import settings
from django.contrib import admin
from django.urls import path

from api.api import api
from core.google_redirect_view import google_redirect_login

urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("api/", api.urls),
    # Plain Django view, not part of the ninja API: Google posts a real HTML form here, not JSON.
    path("google/redirect-login", google_redirect_login),
]

# Only used when DEBUG is off (Django's own debug pages take over otherwise): a stray or probed URL gets the
# same plain JSON the API already answers with, never a Django-branded HTML page.
handler404 = "core.error_views.not_found"
handler500 = "core.error_views.server_error"
