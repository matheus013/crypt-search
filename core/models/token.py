from django.conf import settings
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


class UserToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    token = models.CharField(max_length=512)

    def save(self, *args, **kwargs):
        if not self.pk:
            refresh = RefreshToken.for_user(self.user)
            self.token = str(refresh.access_token)
            self.expires_at = timezone.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at
