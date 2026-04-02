from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from enrollments.models import Enrollment
from .models import Assignment, StudentAssignment
from django.contrib import messages
from django.utils import timezone

@login_required
def student_assignments(request):
    """
    Show all assignments for the student's verified courses with tab filtering.
    """
    tab = request.GET.get('tab', 'all')  # Get the active tab

    # Get all verified enrollments for this student
    verified_enrollments = Enrollment.objects.filter(
        email=request.user.email,
        status='verified'
    )

    # Extract all course IDs
    course_ids = verified_enrollments.values_list('course_id', flat=True)

    # Get assignments for enrolled courses
    assignments = Assignment.objects.filter(course_id__in=course_ids).order_by('-due_date')

    # Fetch all submissions by the student
    submissions = StudentAssignment.objects.filter(student=request.user)
    submission_map = {sub.assignment_id: sub for sub in submissions}

    # Attach submission & deadline check to each assignment
    now = timezone.now()
    for assignment in assignments:
        assignment.submission = submission_map.get(assignment.id)
        assignment.can_submit = now <= assignment.due_date  # True if deadline not passed
        assignment.is_missed = assignment.submission is None and now > assignment.due_date

    # Filter assignments according to selected tab
    if tab == 'submitted':
        assignments = [a for a in assignments if a.submission is not None]
    elif tab == 'missed':
        assignments = [a for a in assignments if a.is_missed]

    context = {
        'assignments': assignments,
        'active_tab': tab,
        'now': now,
    }

    return render(request, 'assignments/student_assignments.html', context)



@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)

    # Check enrollment
    enrollment = Enrollment.objects.filter(
        email=request.user.email,
        course=assignment.course,
        status='verified'
    ).first()
    if not enrollment:
        messages.error(request, "You are not verified or enrolled for this course.")
        return redirect('assignments:student_assignments')

    # Only get existing submission if it exists
    try:
        submission = StudentAssignment.objects.get(assignment=assignment, student=request.user)
    except StudentAssignment.DoesNotExist:
        submission = None

    if request.method == 'POST':
        submission_link = request.POST.get('submission_link', '').strip()

        if not submission_link:
            messages.error(request, "Please provide a valid submission link.")
            return redirect('assignments:submit_assignment', assignment_id=assignment.id)

        # Create or update submission after validating input
        if not submission:
            submission = StudentAssignment(
                assignment=assignment,
                student=request.user,
                submission_link=submission_link,
                status='submitted',
                submitted_at=timezone.now()
            )
        else:
            submission.submission_link = submission_link
            submission.status = 'submitted'
            submission.submitted_at = timezone.now()

        submission.save()
        messages.success(request, "✅ Assignment submitted successfully!")
        return redirect('assignments:student_assignments')

    context = {
        'assignment': assignment,
        'submission': submission,
    }
    return render(request, 'assignments/submit_assignment.html', context)