from django.contrib import admin
from .models import InstructionalRecords, VerificationRequest

@admin.register(InstructionalRecords)
class InstructionalRecordsAdmin(admin.ModelAdmin):
    list_display = ('student', 'program', 'year_level', 'enrollment_status')
    list_filter = ('program', 'year_level', 'enrollment_status')

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ('verification_id', 'student', 'status', 'request_date')
    list_filter = ('status', 'request_date')