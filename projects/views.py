from django.shortcuts import render, get_object_or_404
from .models import Project

# 🖼️ Project Gallery View
def project_gallery(request):
    category = request.GET.get('category')  # Optional category filter
    if category:
        projects = Project.objects.filter(category=category).order_by('-created_at')
    else:
        projects = Project.objects.all().order_by('-created_at')

    categories = Project.CATEGORY_CHOICES
    context = {
        'projects': projects,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'projects/gallery.html', context)