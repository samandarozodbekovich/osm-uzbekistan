from django.conf import settings
from django.contrib.auth import get_user_model, login as django_login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from apps.users.models import PhoneVerification

from .helpers import PENDING_AUTHORIZE_SESSION_KEY, _render_phone_form, _render_code_form

User = get_user_model()


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
