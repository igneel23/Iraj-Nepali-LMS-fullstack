from django.urls import path
from . import views

urlpatterns = [
     path('<uuid:course_id>/recordings/', views.class_recordings, name='class_recordings'),
]