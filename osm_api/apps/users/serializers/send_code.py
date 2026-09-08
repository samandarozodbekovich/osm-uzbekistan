from rest_framework import serializers


class SendCodeSerializer(serializers.Serializer):
    phone_number = serializers.RegexField(
        regex=r'^\+998\d{9}$',
        error_messages={'invalid': 'Format: +998XXXXXXXXX'},
    )
