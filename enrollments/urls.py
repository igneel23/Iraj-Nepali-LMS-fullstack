from django.urls import path
from . import views

urlpatterns = [
    path('enroll/<slug:course_slug>/', views.enroll_course, name='enroll_course'),
]
