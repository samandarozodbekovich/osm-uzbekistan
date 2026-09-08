from rest_framework import serializers

from ..models import PhoneVerification


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
