"""Replaces Django's own 404/500 pages (DEBUG=False only) with the same plain JSON the API already uses,
so a mistyped or probed URL never shows a Django-branded page or template name.
"""

from django.http import JsonResponse


def not_found(request, exception=None):
    return JsonResponse({"detail": "Not found"}, status=404)


def server_error(request):
    return JsonResponse({"detail": "Service unavailable"}, status=500)
