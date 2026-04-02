# attendence/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from enrollments.models import Enrollment
from courses.models import Course
from .models import AttendanceSession, StudentAttendance

@login_required
def student_attendance(request):
    """
    Display all attendance sessions for courses the student is enrolled in,
    along with their attendance status and overall percentage.
    """
    # Get all verified courses the student is enrolled in
    enrolled_courses = Enrollment.objects.filter(
        email=request.user.email,
        status='verified'
    ).select_related('course')

    attendance_data = []

    for enrollment in enrolled_courses:
        course = enrollment.course
        sessions = AttendanceSession.objects.filter(course=course).order_by('-date')
        total_sessions = sessions.count()
        attended_count = StudentAttendance.objects.filter(
            session__in=sessions,
            student=request.user,
            status='present'
        ).count()

        attendance_percentage = 0
        if total_sessions > 0:
            attendance_percentage = round((attended_count / total_sessions) * 100)

        session_list = []
        for session in sessions:
            student_attendance = StudentAttendance.objects.filter(
                session=session,
                student=request.user
            ).first()
            status = student_attendance.status if student_attendance else 'absent'
            session_list.append({
                'title': session.title,
                'date': session.date,
                'status': status
            })

        attendance_data.append({
            'course': course,
            'total_sessions': total_sessions,
            'attended_count': attended_count,
            'percentage': attendance_percentage,
            'sessions': session_list
        })

    context = {
        'attendance_data': attendance_data
    }
    return render(request, 'students/student_attendance.html', context)
