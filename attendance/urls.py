# attendence/urls.py
from django.urls import path
from . import views

app_name = 'attendence'

urlpatterns = [
    # Student view to see their attendance
    path('', views.student_attendance, name='student_attendance'),
]
