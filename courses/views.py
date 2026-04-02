from django.shortcuts import render ,get_object_or_404, redirect
from .models import Course ,Category ,WhatYouWillLearn, Requirement, WhoIsFor, CourseReview
from django.db.models import Q
from enrollments.models import Enrollment

def all_courses(request):
    # Fetch all active & published courses
    courses = Course.objects.filter(is_published=True).order_by('-created_at')
    categories = Category.objects.all().order_by('name')

    # --- Search ---
    query = request.GET.get('q', '')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )

    # --- Category Filter ---
    category_slug = request.GET.get('category', '')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    # --- Sorting ---
    sort_option = request.GET.get('sort', 'latest')
    if sort_option == 'popular':
        courses = courses.order_by('-rating_count', '-rating_avg')
    elif sort_option == 'price_low':
        courses = courses.order_by('discounted_price' if courses.filter(is_discount_active=True).exists() else 'actual_price')
    elif sort_option == 'price_high':
        courses = courses.order_by('-discounted_price' if courses.filter(is_discount_active=True).exists() else '-actual_price')
    else:  # latest
        courses = courses.order_by('-created_at')

    context = {
        'courses': courses,
        'categories': categories,
    }
    return render(request, 'courses/all_courses.html', context)



def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_published=True)

     # Check if the current user is enrolled using email
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(course=course, email=request.user.email).exists()
    
    # Related data
    learning_points = course.learning_points.all()
    requirements = course.requirements.all()
    reviews = course.reviews.select_related('student').all()
    
    context = {
        'course': course,
        'learning_points': learning_points,
        'requirements': requirements,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
    }
    
    # Template path points to main project folder
    return render(request, 'courses/course_detail.html', context)