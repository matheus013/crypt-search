import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class TextVector(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    encrypted_vector = models.BinaryField()
    checksum = models.CharField(max_length=64, null=True)  # Adiciona o campo para o checksum (SHA-256 tem 64 caracteres hex)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"TextVector {self.identifier} for {self.owner}"
