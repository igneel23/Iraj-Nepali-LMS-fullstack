# blogs/views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import BlogPost, BlogCategory ,Comment
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os




#for blog list 
def blog_list(request):
    
    posts = BlogPost.objects.filter(is_published=True, status='published').order_by('-published_at')
    categories = BlogCategory.objects.all().order_by('name')  # fetch all categories
    
    context = {
        'posts': posts,
        'categories': categories
    }
    return render(request, 'blogs/blog_list.html', context)


def blog_detail(request, slug):
    # Fetch the blog post by slug
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Increment views count
    post.views += 1
    post.save(update_fields=['views'])

    # Fetch approved comments for this post
    comments = post.comments.filter(approved=True)

    # Optional: Fetch other posts in the same category for "related posts"
    related_posts = BlogPost.objects.filter(category=post.category, is_published=True).exclude(id=post.id)[:3]

    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
    }

    return render(request, 'blogs/blog_detail.html', context)