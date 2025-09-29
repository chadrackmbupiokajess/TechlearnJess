from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, LoginHistory


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_select_related = ('userprofile',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_time', 'is_successful', 'location']
    list_filter = ['is_successful', 'login_time']
    search_fields = ['user__username', 'user__email', 'ip_address']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'login_time', 'is_successful', 'location']
    ordering = ['-login_time']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)