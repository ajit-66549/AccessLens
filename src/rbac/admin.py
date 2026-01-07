from django.contrib import admin
from .models import Role, RoleAssignment

# Register your models here.
admin.site.register(Role)
admin.site.register(RoleAssignment)