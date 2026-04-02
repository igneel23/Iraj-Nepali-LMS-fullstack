from django.urls import path
from . import views

urlpatterns = [
    path('all-courses/', views.all_courses, name='all_courses'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
]
