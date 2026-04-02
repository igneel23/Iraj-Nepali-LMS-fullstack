from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from enrollments.models import Enrollment
from courses.models import Course
from .models import ClassRecording

@login_required
def class_recordings(request, course_id):
    """
    Display class recordings for a specific enrolled course.
    """
    # Ensure only verified enrolled students can access
    enrollment = Enrollment.objects.filter(
        email=request.user.email,
        course_id=course_id,
        status='verified'
    ).first()

    if not enrollment:
        return render(
            request,
            'students/access_denied.html',
            {'message': "You are not enrolled or verified for this course."}
        )

    course = get_object_or_404(Course, id=course_id)
    recordings = ClassRecording.objects.filter(course=course).order_by('-uploaded_at')

    return render(request, 'classrecordings/view_recordings.html', {
        'course': course,
        'recordings': recordings,
    })
