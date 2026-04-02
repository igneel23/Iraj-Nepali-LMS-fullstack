from django.shortcuts import render
from courses.models import Course, Category
from mentors.models import MentorProfile
from django.template.loader import render_to_string
from django.http import HttpResponse
from projects.models import Project

def index(request):
    categories = Category.objects.all().order_by('name')
    search_query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    courses = Course.objects.filter(is_published=True)

    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    if search_query:
        courses = courses.filter(title__icontains=search_query)

    courses = courses.order_by('-created_at')[:6]

    # Fetch only 8 mentors
    mentors = MentorProfile.objects.select_related('user').all()[:8]

    projects = Project.objects.all().order_by('-created_at')[:6]
    

    # AJAX request returns partial template
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('courses/course_cards_partial.html', {'courses': courses})
        return HttpResponse(html)

    return render(request, 'index.html', {
        'courses': courses,
        'categories': categories,
        'selected_category': category_slug,
        'mentors': mentors,
        'projects': projects, 
    })

def search_courses(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Course.objects.filter(title__icontains=query)  # simple title search
    return render(request, 'courses/search_results.html', {'query': query, 'results': results})