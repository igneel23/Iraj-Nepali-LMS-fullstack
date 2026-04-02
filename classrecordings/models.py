from django.db import models
from django.conf import settings
from courses.models import Course  # import from your existing course app

class ClassRecording(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='recordings')
    title = models.CharField(max_length=255)
    video_url = models.URLField(help_text="Paste YouTube, Vimeo, or Drive video link")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_classrecordings'
    )

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Class Recording"
        verbose_name_plural = "Class Recordings"
