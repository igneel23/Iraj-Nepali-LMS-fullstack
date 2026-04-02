from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from .models import Enrollment
from students.models import StudentProfile

User = get_user_model()


def generate_unique_username(email):
    base_username = email.split("@")[0].lower().replace(" ", "")
    username = base_username
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username


@receiver(post_save, sender=Enrollment)
def create_student_account_on_verification(sender, instance, created, **kwargs):
    # Only work when enrollment is verified
    if instance.status != "verified":
        return

    # If a user with this email already exists, do nothing
    if User.objects.filter(email=instance.email).exists():
        return

    # Create username and random password
    username = generate_unique_username(instance.email)
    password = get_random_string(10)

    # Create student user
    user = User.objects.create_user(
        username=username,
        email=instance.email,
        password=password,
        first_name=instance.first_name,
        last_name=instance.last_name,
        role="student",
    )

    # Create student profile
    StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "phone_number": instance.whatsapp_number,
        }
    )

    # Login URL
    login_url = f"{settings.SITE_URL}/students/login/"

    # Try HTML email template first, fallback to plain email if template missing
    try:
        html_content = render_to_string(
            "students/emails/student_account_created.html",
            {
                "student_name": f"{instance.first_name} {instance.last_name}",
                "email": instance.email,
                "password": password,
                "course": instance.course,
                "login_url": login_url,
            }
        )
        text_content = strip_tags(html_content)

        email_message = EmailMultiAlternatives(
            subject="Your Student Account Has Been Created",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send(fail_silently=False)

    except Exception:
        # Plain text fallback
        from django.core.mail import send_mail

        send_mail(
            subject="Your Student Account Has Been Created",
            message=(
                f"Hello {instance.first_name},\n\n"
                f"Your account for {instance.course.title} has been created.\n\n"
                f"Login Email: {instance.email}\n"
                f"Password: {password}\n"
                f"Login here: {login_url}\n\n"
                f"Please log in and change your password after first login."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            fail_silently=False,
        )