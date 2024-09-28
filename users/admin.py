from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'is_staff', 'is_active')  
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'refresh_token', 'access_token', 'user_permissions')}),
    )

class FriendRequestAdmin(admin.ModelAdmin):
    model = FriendRequest
    list_display = ('id','from_user', 'to_user', 'status', 'created_at')
    search_fields = ('from_user__email', 'to_user__email')
    list_filter = ('status',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
