from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.student_logout, name='logout'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    
    # Dashboard
    path('dashboard/', views.student_dashboard, name='student_dashboard'),

    # Profile
    path('profile/', views.student_profile_view, name='student_profile'),
    path('profile/edit/', views.edit_student_profile, name='edit_student_profile'),

    # Learning
    path('my-learning/', views.my_learning, name='my_learning'),
    path('<uuid:course_id>/player/', views.course_player, name='course_player'),

    # Certificates
    path('my-certificates/', views.student_certificates, name='student_certificates'),
]
