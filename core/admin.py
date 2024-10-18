from django.contrib import admin

from core.models.api_log import APILog
from core.models.container import TextVector


# Register your models here.

@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ('user', 'method', 'path', 'timestamp', 'status_code')
    search_fields = ('user__username', 'path', 'action')


@admin.register(TextVector)
class TextVectorAdmin(admin.ModelAdmin):
    pass
