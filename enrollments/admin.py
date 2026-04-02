from django.contrib import admin
from .models import Enrollment, PendingEnrollment, VerifiedEnrollment


# Default admin for all enrollments
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'whatsapp_number', 'course', 'status', 'created_at')
    list_filter = ('status', 'course')
    search_fields = ('first_name', 'last_name', 'email', 'whatsapp_number')
    ordering = ('-created_at',)


# Shows only pending enrollments
@admin.register(PendingEnrollment)
class PendingEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'course', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status='pending')


# Shows only verified enrollments
@admin.register(VerifiedEnrollment)
class VerifiedEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'course', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status='verified')
