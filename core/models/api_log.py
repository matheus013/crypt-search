# core/models/api_log.py
from django.db import models
from django.contrib.auth.models import User

class APILog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    status_code = models.IntegerField()
    response_data = models.TextField(blank=True, null=True)
    processing_time = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.method} {self.path}"
