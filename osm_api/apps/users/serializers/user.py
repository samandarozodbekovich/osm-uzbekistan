from rest_framework import serializers

from ..models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'phone_number', 'first_name', 'last_name', 'full_name',
                  'is_verified', 'is_active', 'date_joined')
        read_only_fields = ('id', 'phone_number', 'is_verified', 'is_active', 'date_joined')
