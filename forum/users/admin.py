from django.contrib import admin
from .models import User, Role

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'active_role', 'is_active', 'is_staff')
    search_fields = ('email', 'username')
    list_filter = ('is_active', 'is_staff', 'active_role')
    ordering = ('email',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)