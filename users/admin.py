from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role', 'get_department')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'userprofile__role')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__department')
    ordering = ('username',)
    
    def get_role(self, obj):
        return obj.userprofile.get_role_display()
    get_role.short_description = 'Role'
    
    def get_department(self, obj):
        return obj.userprofile.department
    get_department.short_description = 'Department'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Unregister the default User admin
admin.site.unregister(User)
# Register the custom User admin
admin.site.register(User, CustomUserAdmin) 