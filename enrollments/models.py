from django.db import models


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.course.title}"


# ✅ Proxy models for separate admin tables
class PendingEnrollment(Enrollment):
    class Meta:
        proxy = True
        verbose_name = "Enrollment Request (Pending)"
        verbose_name_plural = "Enrollment Requests (Pending)"


class VerifiedEnrollment(Enrollment):
    class Meta:
        proxy = True
        verbose_name = "Verified Enrollment"
        verbose_name_plural = "Verified Enrollments"
