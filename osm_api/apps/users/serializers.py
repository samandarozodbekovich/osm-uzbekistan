from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, PhoneVerification


class SendCodeSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(
        regex=r'^\+998\d{9}$',
        error_messages={'invalid': 'Format: +998XXXXXXXXX'},
    )


class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(regex=r'^\+998\d{9}$')
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, data):
        phone = data['phone_number']
        code = data['code']

        verification = (
            PhoneVerification.objects
            .filter(phone_number=phone, is_used=False)
            .order_by('-created_at')
            .first()
        )

        if not verification:
            raise serializers.ValidationError('Tasdiqlash kodi topilmadi.')
        if verification.is_expired:
            raise serializers.ValidationError('Kod muddati tugagan. Qayta yuborish.')
        if verification.attempts >= 3:
            raise serializers.ValidationError('Juda ko\'p urinish. Qayta kod oling.')

        verification.attempts += 1
        verification.save(update_fields=['attempts'])

        if verification.code != code:
            raise serializers.ValidationError('Noto\'g\'ri kod.')

        verification.is_used = True
        verification.save(update_fields=['is_used'])

        data['phone_number'] = phone
        return data


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'full_name',
                  'is_verified', 'is_active', 'date_joined')
        read_only_fields = ('id', 'phone_number', 'is_verified', 'is_active', 'date_joined')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

    @classmethod
    def for_user(cls, user):
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }
