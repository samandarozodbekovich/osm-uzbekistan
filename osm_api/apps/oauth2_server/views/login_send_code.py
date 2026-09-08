from django.conf import settings
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from apps.users.models import PhoneVerification

from .helpers import _render_phone_form, _render_code_form


@method_decorator(csrf_protect, name="dispatch")
class LoginSendCodeView(View):
    def post(self, request):
        phone_number = request.POST.get("phone_number", "").strip()
        if not phone_number:
            return _render_phone_form(request, error="Phone number is required.")

        verification = PhoneVerification.create_for(phone_number)
        debug_code = verification.code if settings.DEBUG else None

        return _render_code_form(request, phone_number, debug_code=debug_code)
