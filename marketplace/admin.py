from django.contrib import admin
from .models import Resource, ResourceImage

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'price', 'condition', 'status', 'date_posted')
    list_filter = ('status', 'condition', 'category')

@admin.register(ResourceImage)
class ResourceImageAdmin(admin.ModelAdmin):
    list_display = ('resource', 'display_order', 'is_primary')