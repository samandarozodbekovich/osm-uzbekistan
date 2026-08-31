from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SendCodeView, VerifyCodeView,
    UserProfileView, UserDeleteView,
    UserViewSet,
)

router = SimpleRouter()
router.register('list', UserViewSet, basename='user')

urlpatterns = [
    # Auth
    path('auth/send-code/', SendCodeView.as_view(), name='send-code'),
    path('auth/verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # Profile
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('me/delete/', UserDeleteView.as_view(), name='user-delete'),
] + router.urls
