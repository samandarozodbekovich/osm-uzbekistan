from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import CustomUser
from ..serializers import VerifyCodeSerializer, TokenResponseSerializer


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
