from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'resource', 'reason', 'status', 'date_reported')
    list_filter = ('status', 'reason')