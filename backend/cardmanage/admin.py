from django.contrib import admin
from .models import Card, IDCardPrintLog, IDCardVerificationLog

# Register your models here.
admin.site.register(Card)


@admin.register(IDCardPrintLog)
class IDCardPrintLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'printed_by', 'user_type', 'printed_at', 'pdf_generated']
    list_filter = ['printed_at', 'user_type', 'pdf_generated']
    search_fields = ['student__registration_number', 'student__first_name', 'student__surname', 'printed_by']
    readonly_fields = ['printed_at']
    date_hierarchy = 'printed_at'


@admin.register(IDCardVerificationLog)
class IDCardVerificationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'verified_at', 'ip_address', 'verification_source']
    list_filter = ['verified_at', 'verification_source']
    search_fields = ['student__registration_number', 'student__first_name', 'student__surname', 'ip_address']
    readonly_fields = ['verified_at']
    date_hierarchy = 'verified_at'
