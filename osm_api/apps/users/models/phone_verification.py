import random
from datetime import timedelta

from django.db import models
from django.utils import timezone


class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'phone_verifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone_number} — {self.code}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def create_for(cls, phone_number):
        cls.objects.filter(phone_number=phone_number, is_used=False).update(is_used=True)
        code = str(random.randint(100000, 999999))
        return cls.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5),
        )
