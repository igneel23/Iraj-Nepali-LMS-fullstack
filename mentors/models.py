from django.db import models
from django.conf import settings
import uuid

class MentorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentor_profile')
    mentor_id = models.CharField(max_length=20, unique=True, default='', editable=False)
    photo = models.ImageField(upload_to='mentors/photos/', blank=True, null=True)
    expertise = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    experience = models.PositiveIntegerField(default=0, help_text="Years of professional experience")
    current_company = models.CharField(max_length=255, blank=True, help_text="Current company or organization name")
    joined_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.mentor_id:
            self.mentor_id = f"MTR-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.mentor_id})"
