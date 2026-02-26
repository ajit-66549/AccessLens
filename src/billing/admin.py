from django.contrib import admin
from .models import Plan, OrganizationSubscription, UsageRecord
# Register your models here.

admin.site.register(Plan)
admin.site.register(OrganizationSubscription)
admin.site.register(UsageRecord)