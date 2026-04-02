from django.db import models
from django.conf import settings
from courses.models import Course
import uuid

class Certificate(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_file = models.FileField(blank=True ,upload_to='certificates/templates/')
    issue_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)  # Admin publishes the certificate

    def __str__(self):
        return f"{self.title} - {self.course.title}"



class StudentCertificate(models.Model):
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='student_certificates')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    issued_on = models.DateTimeField(auto_now_add=True)
    unique_id = models.CharField(max_length=12, unique=True, editable=False)
    download_link = models.CharField(max_length=300, blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('issued', 'Issued'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        import uuid
        if not self.unique_id:
            self.unique_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
