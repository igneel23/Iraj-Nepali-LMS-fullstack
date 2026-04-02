# attendence/admin.py
from django.contrib import admin
from .models import AttendanceSession, StudentAttendance

class StudentAttendanceInline(admin.TabularInline):
    """
    Allows marking student attendance directly inside the session page.
    """
    model = StudentAttendance
    extra = 0
    fields = ('student', 'status', 'marked_at')
    readonly_fields = ('marked_at',)
    autocomplete_fields = ('student',)


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'date', 'start_time', 'end_time')
    list_filter = ('course', 'date')
    search_fields = ('title', 'course__title')
    inlines = [StudentAttendanceInline]
    ordering = ('-date',)
    list_per_page = 20


@admin.register(StudentAttendance)
class StudentAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_at')
    list_filter = ('status', 'session__course')
    search_fields = ('student__username', 'student__email', 'session__title', 'session__course__title')
    ordering = ('-marked_at',)
    list_per_page = 50
