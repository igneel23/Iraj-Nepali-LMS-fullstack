from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from users.models import User
from students.models import StudentProfile
from mentors.models import MentorProfile

DEFAULT_STUDENT_PASSWORD = "student@123"
DEFAULT_MENTOR_PASSWORD = "mentor@123"

def send_student_welcome_email(student, password):
    """
    Sends a well-styled welcome email to the student.
    """
    html_content = render_to_string('students/emails/welcome_email.html', {
        'student': student,
        'password': password,
        'login_url': 'http://127.0.0.1:8000/students/login/'  # Change to your domain
    })
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject="Welcome to Our LMS Platform",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[student.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=True)


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if not created:
        return
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
            if not instance.has_usable_password():
                instance.set_password(DEFAULT_STUDENT_PASSWORD)
                instance.save(update_fields=['password'])
            # Send welcome email
            send_student_welcome_email(instance, DEFAULT_STUDENT_PASSWORD)

        elif instance.role == 'mentor':
            MentorProfile.objects.create(user=instance)
            if not instance.has_usable_password():
                instance.set_password(DEFAULT_MENTOR_PASSWORD)
                instance.save(update_fields=['password'])
