from django.shortcuts import render
from .models import MentorProfile

def mentor_list(request):
    mentors = MentorProfile.objects.select_related('user').all()

    return render(request, 'mentors/mentor_list.html', {
        'mentors': mentors,
    })