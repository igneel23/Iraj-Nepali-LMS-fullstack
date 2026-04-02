from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import logout
import os
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from enrollments.models import Enrollment
from classrecordings.models import ClassRecording
from courses.models import Course
import re
from certificates.models import StudentCertificate
from assignments.models import StudentAssignment
from attendance.models import StudentAttendance
from .models import StudentProfile
from django.contrib import messages
from .forms import StudentProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.timezone import now

User = get_user_model()


def student_login(request):
    if request.user.is_authenticated and getattr(request.user, 'role', '') == 'student':
        return redirect('student_dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.role == 'student':  # to ensure only students can log in here
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('student_dashboard')  # student dashboard
            else:
                messages.error(request, "Access denied. You are not a student.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'students/login.html')


@login_required
def student_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('student_login')


@login_required
def change_password(request):
    """
    Allows a logged-in student to change their password.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps user logged in
            messages.success(request, "✅ Your password was changed successfully.")
            return redirect('student_profile')
        else:
            messages.error(request, "❌ Please correct the errors below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'students/change_password.html', {'form': form})


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            # Generate token
            token = default_token_generator.make_token(user)

            # Store token and user ID in session
            request.session['reset_user_id'] = user.id
            request.session['reset_token'] = token

            # Build reset URL
            reset_url = request.build_absolute_uri(
                reverse('reset_password', kwargs={'token': token})
            )

            # Render HTML email template
            html_content = render_to_string('students/emails/forgot_password_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            text_content = strip_tags(html_content)  # Fallback for plain text email

            # Send email
            email_message = EmailMultiAlternatives(
                subject="Reset Your Password",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
            )
            email_message.attach_alternative(html_content, "text/html")
            email_message.send(fail_silently=False)

            messages.success(request, "Password reset link has been sent to your email.")
            return redirect('forgot_password')

        except User.DoesNotExist:
            messages.error(request, "No user found with this email.")

    return render(request, 'students/forgot_password.html')



def reset_password(request, token):
    user_id = request.session.get('reset_user_id')
    session_token = request.session.get('reset_token')

    if not user_id or not session_token or session_token != token:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('forgot_password')

    user = User.objects.get(id=user_id)

    if request.method == "POST":
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if new_password1 != new_password2:
            messages.error(request, "Passwords do not match.")
        elif not new_password1:
            messages.error(request, "Password cannot be empty.")
        else:
            user.set_password(new_password1)
            user.save()
            messages.success(request, "Your password has been reset successfully!")

            # Clear session
            request.session.pop('reset_user_id')
            request.session.pop('reset_token')

            return redirect('student_login')

    return render(request, 'students/reset_password.html', {'token': token})


@login_required
def student_profile_view(request):
    # Get the logged-in user's student profile
    profile = get_object_or_404(StudentProfile, user=request.user)
    
    context = {
        'profile': profile
    }
    return render(request, 'students/student_profile.html', context)

@login_required
def edit_student_profile(request):
    # Get the student's profile (create if missing)
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            # Save both profile + user data
            profile = form.save(commit=False)
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.email = form.cleaned_data.get('email')
            request.user.save()
            profile.save()
            messages.success(request, "✅ Profile updated successfully!")
            return redirect('student_profile')
    else:
        # Pre-fill form with user + profile data
        form = StudentProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'username': request.user.username,
        })

    return render(request, 'students/edit_student_profile.html', {'form': form})

@login_required
def student_dashboard(request):
    user = request.user

    # Get enrolled courses (verified only)
    enrollments = Enrollment.objects.filter(email=user.email, status='verified').select_related('course')
    enrolled_courses = [en.course for en in enrollments]  # list of actual Course objects

    # Filter related data safely
    recent_assignments = StudentAssignment.objects.filter(student=user).order_by('-submitted_at')[:5]
    recent_attendance = StudentAttendance.objects.filter(student=user).order_by('-marked_at')[:5]
    certificates = StudentCertificate.objects.filter(student=user, status='issued')

    # Stats
    total_courses = len(enrolled_courses)
    total_assignments = StudentAssignment.objects.filter(student=user).count()
    completed_assignments = StudentAssignment.objects.filter(student=user, status='submitted').count()

    # Percentages
    assignments_percentage = (
        (completed_assignments / total_assignments) * 100 if total_assignments > 0 else 0
    )
    attendance_percentage = (
        (StudentAttendance.objects.filter(student=user, status='present').count() /
         StudentAttendance.objects.filter(student=user).count()) * 100
        if StudentAttendance.objects.filter(student=user).exists() else 0
    )

    context = {
        'enrollments': enrollments,
        'enrolled_courses': enrolled_courses,
        'recent_assignments': recent_assignments,
        'recent_attendance': recent_attendance,
        'certificates': certificates,
        'total_courses': total_courses,
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'assignments_percentage': round(assignments_percentage, 2),
        'attendance_percentage': round(attendance_percentage, 2),
    }

    return render(request, 'students/student_dashboard.html', context)



@login_required
def my_learning(request):
    user_email = request.user.email
    enrolled_courses = Enrollment.objects.filter(
        email=user_email, status='verified'
    ).select_related('course')

    return render(request, 'students/my_learning.html', {
        'enrolled_courses': enrolled_courses
    })




def course_player(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    recordings = ClassRecording.objects.filter(course=course).order_by("uploaded_at")

    video_id = request.GET.get("video")
    current_video = recordings.filter(id=video_id).first() if video_id else recordings.first()

    def get_embed_url(url):
        import re
        yt_match = re.search(r"(?:v=|youtu\.be/)([\w\-]{11})", url)
        if yt_match:
            return f"https://www.youtube.com/embed/{yt_match.group(1)}"
        vimeo_match = re.search(r"vimeo\.com/(\d+)", url)
        if vimeo_match:
            return f"https://player.vimeo.com/video/{vimeo_match.group(1)}"
        drive_match = re.search(r"file/d/([a-zA-Z0-9_-]+)", url)
        if drive_match:
            return f"https://drive.google.com/file/d/{drive_match.group(1)}/preview"
        if url.endswith(".mp4"):
            return url
        return None

    embed_url = get_embed_url(current_video.video_url) if current_video else None
    is_mp4 = embed_url and embed_url.endswith(".mp4")

    return render(request, "students/course_player.html", {
        "course": course,
        "recordings": recordings,
        "current_video": current_video,
        "embed_url": embed_url,
        "is_mp4": is_mp4,
    })


@login_required
def student_certificates(request):

    # Get issued certificates for logged-in student
    student_certificates = StudentCertificate.objects.filter(student=request.user, status='issued')

    # Add full URL for downloading
    for cert in student_certificates:
        if cert.download_link:
            cert.download_url = f"{settings.MEDIA_URL}{cert.download_link}"
        else:
            cert.download_url = None

    return render(request, 'students/student_certificates.html', {
        'student_certificates': student_certificates
    })



def send_certificate_email(student_certificate_id):
    certificate = StudentCertificate.objects.get(id=student_certificate_id)
    student = certificate.student
    course = certificate.course

    # Build full URLs
    login_url = f"{settings.SITE_URL}/students/login/"
    cert_url = f"{settings.MEDIA_URL}{certificate.download_link}" if certificate.download_link else None

    # Render HTML email template
    html_content = render_to_string('students/emails/certificate_published_email.html', {
        'student': student,
        'certificate': certificate,
        'cert_url': cert_url,
        'login_url': login_url,
        'now': now(),
    })
    text_content = strip_tags(html_content)

    # Create email
    email = EmailMultiAlternatives(
        subject=f"Your Certificate for {course.title} is Ready!",
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[student.email]
    )

    email.attach_alternative(html_content, "text/html")

    # Attach PDF if available
    if certificate.download_link:
        pdf_path = os.path.join(settings.MEDIA_ROOT, certificate.download_link)
        if os.path.exists(pdf_path):
            email.attach_file(pdf_path)

    email.send(fail_silently=False)

