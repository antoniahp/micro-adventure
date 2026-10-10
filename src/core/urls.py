from django.conf import settings
from django.contrib import admin
from django.urls import path

from api.api import api

urlpatterns = [
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("api/", api.urls),
]

# Only used when DEBUG is off (Django's own debug pages take over otherwise): a stray or probed URL gets the
# same plain JSON the API already answers with, never a Django-branded HTML page.
handler404 = "core.error_views.not_found"
handler500 = "core.error_views.server_error"
