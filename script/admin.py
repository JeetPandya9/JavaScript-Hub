from django.contrib import admin
from .models import User, Contact, Course, Module, Lesson, Enrollment, LessonProgress

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'email', 'created_at')
    search_fields = ('firstname', 'lastname', 'email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'duration_hours', 'is_free', 'created_at')
    list_filter = ('difficulty', 'is_free', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('course', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'duration_minutes', 'order', 'created_at')
    list_filter = ('module__course', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('module__course', 'module__order', 'order')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed_at', 'is_active')
    list_filter = ('course', 'enrolled_at', 'completed_at', 'is_active')
    search_fields = ('user__firstname', 'user__lastname', 'course__title')
    readonly_fields = ('enrolled_at',)
    ordering = ('-enrolled_at',)

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'is_completed', 'progress_percentage', 'completed_at')
    list_filter = ('is_completed', 'completed_at', 'lesson__module__course')
    search_fields = ('user__firstname', 'user__lastname', 'lesson__title')
    readonly_fields = ('completed_at',)
    ordering = ('-completed_at',)
