from urllib.parse import urlencode

from django.contrib.auth import get_user_model, login as django_login
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import PhoneVerification

from .models import OAuthClient, AuthorizationCode
from .pkce import verify_code_verifier

User = get_user_model()

PENDING_AUTHORIZE_SESSION_KEY = "oauth2_pending_authorize_qs"


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


class TokenView(APIView):
    """
    POST /oauth2/token

    The osm-auth client library sends token request parameters as URL
    query parameters even though the method is POST (not as a form-encoded
    body). We accept both to be safe: body values take precedence if a
    field appears in both places.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        def get_param(name):
            return request.data.get(name) or request.query_params.get(name)

        grant_type = get_param("grant_type")
        if grant_type != "authorization_code":
            return Response({"error": "unsupported_grant_type"}, status=400)

        code = get_param("code")
        redirect_uri = get_param("redirect_uri")
        client_id = get_param("client_id")
        code_verifier = get_param("code_verifier")

        try:
            auth_code = AuthorizationCode.objects.select_related("client", "user").get(code=code)
        except AuthorizationCode.DoesNotExist:
            return Response({"error": "invalid_grant"}, status=400)

        if auth_code.used or auth_code.is_expired():
            return Response({"error": "invalid_grant", "detail": "code expired or already used"}, status=400)

        if auth_code.client.client_id != client_id:
            return Response({"error": "invalid_client"}, status=400)

        if auth_code.redirect_uri != redirect_uri:
            return Response({"error": "invalid_grant", "detail": "redirect_uri mismatch"}, status=400)

        if not verify_code_verifier(code_verifier, auth_code.code_challenge, auth_code.code_challenge_method):
            return Response({"error": "invalid_grant", "detail": "PKCE verification failed"}, status=400)

        auth_code.used = True
        auth_code.save(update_fields=["used"])

        refresh = RefreshToken.for_user(auth_code.user)
        access = refresh.access_token

        return Response({
            "access_token": str(access),
            "token_type": "Bearer",
            "expires_in": int(access.lifetime.total_seconds()),
            "refresh_token": str(refresh),
            "scope": "read_prefs write_api",
        })


# ---------------------------------------------------------------------------
# Minimal phone + OTP login used only to establish a Django session for the
# /oauth2/authorize step above.
# ---------------------------------------------------------------------------

def _render_phone_form(request, error=None):
    csrf_token = get_token(request)
    error_html = f'<p style="color:red">{error}</p>' if error else ""
    return HttpResponse(f"""
        <html><body style="font-family: sans-serif; max-width: 400px; margin: 60px auto;">
            <h2>Sign in to continue</h2>
            {error_html}
            <form method="post" action="{reverse('oauth2-login-send-code')}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <label>Phone number (+998XXXXXXXXX)</label><br>
                <input type="text" name="phone_number" placeholder="+998901234567" required style="width:100%; padding:8px; margin:8px 0;">
                <button type="submit" style="padding:8px 16px;">Send code</button>
            </form>
        </body></html>
    """)


def _render_code_form(request, phone_number, debug_code=None, error=None):
    csrf_token = get_token(request)
    error_html = f'<p style="color:red">{error}</p>' if error else ""
    debug_html = f'<p style="color:gray">Dev code: {debug_code}</p>' if debug_code else ""
    return HttpResponse(f"""
        <html><body style="font-family: sans-serif; max-width: 400px; margin: 60px auto;">
            <h2>Enter the code sent to {phone_number}</h2>
            {debug_html}
            {error_html}
            <form method="post" action="{reverse('oauth2-login-verify-code')}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <input type="hidden" name="phone_number" value="{phone_number}">
                <label>6-digit code</label><br>
                <input type="text" name="code" maxlength="6" required style="width:100%; padding:8px; margin:8px 0;">
                <button type="submit" style="padding:8px 16px;">Verify</button>
            </form>
        </body></html>
    """)


@method_decorator(csrf_protect, name="dispatch")
class LoginPageView(View):
    def get(self, request):
        if PENDING_AUTHORIZE_SESSION_KEY not in request.session:
            return HttpResponse("No pending authorization request.", status=400)
        return _render_phone_form(request)


@method_decorator(csrf_protect, name="dispatch")
class LoginSendCodeView(View):
    def post(self, request):
        phone_number = request.POST.get("phone_number", "").strip()
        if not phone_number:
            return _render_phone_form(request, error="Phone number is required.")

        verification = PhoneVerification.create_for(phone_number)
        debug_code = verification.code if settings.DEBUG else None

        return _render_code_form(request, phone_number, debug_code=debug_code)


@method_decorator(csrf_protect, name="dispatch")
class LoginVerifyCodeView(View):
    def post(self, request):
        phone_number = request.POST.get("phone_number", "").strip()
        code = request.POST.get("code", "").strip()

        verification = (
            PhoneVerification.objects
            .filter(phone_number=phone_number, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not verification or verification.is_expired or verification.attempts >= 3:
            return _render_phone_form(request, error="Code expired or too many attempts — request a new one.")

        verification.attempts += 1
        verification.save(update_fields=["attempts"])

        if verification.code != code:
            return _render_code_form(request, phone_number, error="Incorrect code.")

        verification.is_used = True
        verification.save(update_fields=["is_used"])

        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={"is_verified": True},
        )
        if not created and not user.is_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        user.backend = "django.contrib.auth.backends.ModelBackend"
        django_login(request, user)

        pending_qs = request.session.pop(PENDING_AUTHORIZE_SESSION_KEY, "")
        return redirect(f"{reverse('oauth2-authorize')}?{pending_qs}")