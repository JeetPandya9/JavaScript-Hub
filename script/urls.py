from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('junior-courses/', views.junior_courses, name='junior_courses'),
    path('intermediate-courses/', views.intermediate_courses, name='intermediate_courses'),
    path('advanced-courses/', views.advanced_courses, name='advanced_courses'),
    path('video-tutorials/', views.video_tutorials, name='video_tutorials'),
    path('code-examples/', views.code_examples, name='code_examples'),
    path('practice-exercises/', views.practice_exercises, name='practice_exercises'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    
    # New enrollment and learning URLs
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('update-progress/<int:lesson_id>/', views.update_lesson_progress, name='update_lesson_progress'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-courses/', views.my_courses, name='my_courses'),
    
    # Social Authentication URLs
    path('auth/google/', views.google_auth, name='google_auth'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path('auth/github/', views.github_auth, name='github_auth'),
    path('auth/github/callback/', views.github_callback, name='github_callback'),
]
