from django.urls import path
from .views import (
    AuthorizeView, TokenView,
    LoginPageView, LoginSendCodeView, LoginVerifyCodeView,
)

urlpatterns = [
    path("authorize", AuthorizeView.as_view(), name="oauth2-authorize"),
    path("token", TokenView.as_view(), name="oauth2-token"),

    path("login", LoginPageView.as_view(), name="oauth2-login"),
    path("login/send-code", LoginSendCodeView.as_view(), name="oauth2-login-send-code"),
    path("login/verify-code", LoginVerifyCodeView.as_view(), name="oauth2-login-verify-code"),
]