from django.contrib import admin
from .models import App, Apikey

# Register your models here.
admin.site.register(App)

admin.site.register(Apikey)

class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "app", "name", "is_active", "created_at", "revoked_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "app__name", "app__key")