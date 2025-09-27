from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'type')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'type', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_staff')
    list_filter = ('type', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Rest of the admin registrations remain the same...
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_verified')
    list_filter = ('is_verified',)

@admin.register(InstructionalRecords)
class InstructionalRecordsAdmin(admin.ModelAdmin):
    list_display = ('student', 'program', 'year_level', 'enrollment_status')
    list_filter = ('program', 'year_level', 'enrollment_status')

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('verification_id', 'student', 'status', 'request_date')
    list_filter = ('status', 'request_date')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'parent_category', 'is_active')
    list_filter = ('is_active',)

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'price', 'condition', 'status', 'date_posted')
    list_filter = ('status', 'condition', 'category')

@admin.register(ResourceImage)
class ResourceImageAdmin(admin.ModelAdmin):
    list_display = ('resource', 'display_order', 'is_primary')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'resource', 'reason', 'status', 'date_reported')
    list_filter = ('status', 'reason')

admin.site.register(User, CustomUserAdmin)