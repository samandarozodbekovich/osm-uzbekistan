from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.urls import reverse

PENDING_AUTHORIZE_SESSION_KEY = "oauth2_pending_authorize_qs"


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
