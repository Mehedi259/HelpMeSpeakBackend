from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Token, PasswordResetSession, SubscriptionPlan, Profile
from django.utils.translation import gettext_lazy as _

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    # Fields to display in the admin list view
    list_display = ('email', 'full_name', 'role', 'is_email_verified', 'is_2fa_enabled', 'is_active', 'created_at')
    list_filter = ('role', 'is_email_verified', 'is_2fa_enabled', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('full_name', 'gender')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'is_email_verified', 'is_2fa_enabled')}),
        (_('Important Dates'), {'fields': ('last_login', 'created_at')}),
        (_('Verification'), {'fields': ('email_verification_code', 'email_verification_code_expires_at')}),
        (_('Password Reset'), {'fields': ('password_reset_code', 'password_reset_code_expires_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'role', 'is_email_verified', 'is_2fa_enabled'),
        }),
    )
    filter_horizontal = ()
    readonly_fields = ('created_at', 'last_login')

    # Custom action to mark users as email verified
    actions = ['mark_email_verified']

    def mark_email_verified(self, request, queryset):
        queryset.update(is_email_verified=True, is_active=True, email_verification_code=None, email_verification_code_expires_at=None)
        self.message_user(request, "Selected users' emails have been marked as verified.")
    mark_email_verified.short_description = "Mark selected users' emails as verified"

# Token Admin
class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'access_token_expires_at', 'refresh_token_expires_at', 'revoked', 'created_at')
    list_filter = ('revoked',)
    search_fields = ('user__email', 'email')
    readonly_fields = ('created_at',)
    actions = ['revoke_tokens']

    def revoke_tokens(self, request, queryset):
        queryset.update(revoked=True)
        self.message_user(request, "Selected tokens have been revoked.")
    revoke_tokens.short_description = "Revoke selected tokens"

# PasswordResetSession Admin
class PasswordResetSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_expired')
    search_fields = ('user__email', 'token')
    readonly_fields = ('created_at',)

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired"

# SubscriptionPlan Admin
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    ordering = ('price',)

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'phone', 'created_at', 'updated_at')
    search_fields = ('user__email', 'employee_id', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('created_at',)

# Register models with the admin site
admin.site.register(User, UserAdmin)
admin.site.register(Token, TokenAdmin)
admin.site.register(PasswordResetSession, PasswordResetSessionAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Profile, ProfileAdmin)