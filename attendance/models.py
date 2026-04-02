# attendence/models.py
from django.db import models
from django.conf import settings
from courses.models import Course

class AttendanceSession(models.Model):
    """
    Represents a single session (class) for a course where attendance is taken.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    title = models.CharField(max_length=200, blank=True, null=True)  # e.g., "Lecture 1", "Week 3 Class"
    date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)  # Optional notes about the session

    class Meta:
        ordering = ['-date', 'start_time']
        verbose_name = "Attendance Session"
        verbose_name_plural = "Attendance Sessions"

    def __str__(self):
        return f"{self.course.title} - {self.title or self.date}"


class StudentAttendance(models.Model):
    """
    Stores the attendance status of a student for a particular session.
    """
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    marked_at = models.DateTimeField(auto_now_add=True)  # When the attendance was recorded

    class Meta:
        unique_together = ('session', 'student')
        ordering = ['session__date', 'student__username']
        verbose_name = "Student Attendance"
        verbose_name_plural = "Student Attendances"

    def __str__(self):
        return f"{self.student.username} - {self.session} ({self.status})"
