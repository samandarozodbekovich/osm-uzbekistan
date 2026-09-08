from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import AuthorizationCode
from ..pkce import verify_code_verifier


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
