from django.contrib import admin
from .models import Assignment, StudentAssignment

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date')
    list_filter = ('course',)
    search_fields = ('title', 'description')


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'marks_obtained', 'submitted_at')
    list_filter = ('status', 'assignment')
    search_fields = ('student__username', 'assignment__title')
