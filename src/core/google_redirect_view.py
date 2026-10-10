"""Receives the POST Google sends back after "Sign in with Google" in redirect mode.

The popup mode (window.open) that Google Identity Services uses by default is unreliable inside an
installed PWA: a popup opened from a standalone-display app window can end up blank and stuck instead
of showing Google's account picker. Redirect mode avoids the popup entirely - the whole page navigates
to Google and back - which works the same inside an installed app as in an ordinary browser tab.

Google's redirect flow posts here as a normal (non-JSON) form, not an XHR, so this has to be a real
Django view, not part of the django-ninja API. It hands the credential back to the page in the URL
fragment (never sent to any server, including ours, on the next request) rather than an inline
<script>, which the CSP's script-src would otherwise block. The existing linking code (the same one
the popup flow already used) reads that fragment on load and calls the account API exactly as before.
"""

from urllib.parse import quote

from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def google_redirect_login(request):
    # Google's own CSRF check for this flow: it sets a g_csrf_token cookie and posts the same value
    # back in the form body. A mismatch (or a missing one) means the POST didn't really come from the
    # sign-in flow we started, so it's refused rather than trusted.
    cookie_token = request.COOKIES.get("g_csrf_token")
    posted_token = request.POST.get("g_csrf_token")
    if not cookie_token or not posted_token or cookie_token != posted_token:
        return HttpResponseBadRequest("Invalid CSRF token")

    credential = quote(request.POST.get("credential", ""), safe="")
    return HttpResponseRedirect(f"/#google_credential={credential}")
