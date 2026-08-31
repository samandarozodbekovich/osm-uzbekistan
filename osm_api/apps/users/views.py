from django.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import CustomUser, PhoneVerification
from .serializers import (
    SendCodeSerializer, VerifyCodeSerializer,
    UserSerializer, UserUpdateSerializer, TokenResponseSerializer,
)


class SendCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        verification = PhoneVerification.create_for(phone)

        response = {'message': 'Tasdiqlash kodi yuborildi.', 'expires_in': 300}
        if settings.DEBUG:
            response['code'] = verification.code

        return Response(response, status=status.HTTP_200_OK)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone_number']
        user, created = CustomUser.objects.get_or_create(
            phone_number=phone,
            defaults={'is_verified': True},
        )
        if not created and not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified'])

        tokens = TokenResponseSerializer.for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)


class UserProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class UserDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'message': 'Hisob o\'chirildi.'}, status=status.HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """Admin uchun — barcha userlarni boshqarish."""
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        return Response({'status': 'deactivated'})

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save(update_fields=['is_active'])
        return Response({'status': 'activated'})
