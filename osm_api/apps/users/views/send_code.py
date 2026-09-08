from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import PhoneVerification
from ..serializers import SendCodeSerializer


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
