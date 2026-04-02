from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    # View all assignments for the logged-in student
    path('', views.student_assignments, name='student_assignments'),
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),

]
