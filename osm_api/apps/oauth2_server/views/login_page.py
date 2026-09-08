from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect

from .helpers import PENDING_AUTHORIZE_SESSION_KEY, _render_phone_form


@method_decorator(csrf_protect, name="dispatch")
class LoginPageView(View):
    def get(self, request):
        if PENDING_AUTHORIZE_SESSION_KEY not in request.session:
            return HttpResponse("No pending authorization request.", status=400)
        return _render_phone_form(request)
