from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from courses.models import Course
from .models import Enrollment

def enroll_course(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    context = {'course': course, 'enrolled': False, 'enrollment_status': None}

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        whatsapp_number = request.POST.get('whatsapp_number')

        # Check if email is already enrolled for this course
        enrollment = Enrollment.objects.filter(email=email, course=course).first()
        if enrollment:
            # Already submitted enrollment
            messages.info(
                request,
                f"The email {email} has already submitted enrollment for this course. "
                f"Current status: {enrollment.get_status_display()}."
            )
            context['enrolled'] = True
            context['enrollment_status'] = enrollment.get_status_display()
        else:
            # Create new enrollment as pending
            Enrollment.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                whatsapp_number=whatsapp_number,
                course=course,
                status='pending'
            )
            messages.success(
                request,
                "Your enrollment has been submitted and is pending verification by admin."
            )
            context['enrolled'] = True
            context['enrollment_status'] = "Pending"

    return render(request, 'enrollments/enroll.html', context)
