from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from ..models import OAuthClient, AuthorizationCode
from .helpers import PENDING_AUTHORIZE_SESSION_KEY


@method_decorator(csrf_protect, name="dispatch")
class AuthorizeView(View):
    """
    GET /oauth2/authorize

    Plain Django View (not DRF APIView) on purpose: DRF's request.user
    is resolved through its own configured authentication classes (e.g.
    JWTAuthentication) and ignores the plain Django session set by
    django.contrib.auth.login(). Using a plain View here means
    request.user comes from AuthenticationMiddleware + the session,
    which is exactly what we need after the phone+OTP login below.
    """

    def get(self, request):
        if not request.user.is_authenticated:
            request.session[PENDING_AUTHORIZE_SESSION_KEY] = request.META.get("QUERY_STRING", "")
            return redirect(reverse("oauth2-login"))

        client_id = request.GET.get("client_id")
        redirect_uri = request.GET.get("redirect_uri")
        code_challenge = request.GET.get("code_challenge")
        code_challenge_method = request.GET.get("code_challenge_method", "S256")
        state = request.GET.get("state", "")

        try:
            client = OAuthClient.objects.get(client_id=client_id)
        except OAuthClient.DoesNotExist:
            return HttpResponse("invalid_client", status=400)

        if not client.allows_redirect_uri(redirect_uri):
            return HttpResponse("invalid_redirect_uri", status=400)

        if not code_challenge:
            return HttpResponse("missing_code_challenge", status=400)

        auth_code = AuthorizationCode.objects.create(
            client=client,
            user=request.user,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )

        query = urlencode({"code": auth_code.code, "state": state})
        return redirect(f"{redirect_uri}?{query}")
