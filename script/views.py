from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
import requests
from urllib.parse import urlencode, parse_qs
import json
import secrets
from .models import User, Contact, Course, Module, Lesson, Enrollment, LessonProgress

# Create your views here.
def home(request):
    # Get featured courses
    featured_courses = Course.objects.all()[:6]
    context = {
        'featured_courses': featured_courses
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message')
        
        if name and email and message:
            Contact.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            return redirect('contact')
    
    return render(request, 'contact.html')

def junior_courses(request):
    courses = Course.objects.filter(difficulty='junior')
    context = {
        'courses': courses,
        'difficulty': 'junior'
    }
    return render(request, 'junior_course.html', context)

def intermediate_courses(request):
    courses = Course.objects.filter(difficulty='intermediate')
    context = {
        'courses': courses,
        'difficulty': 'intermediate'
    }
    return render(request, 'intermediate_course.html', context)

def advanced_courses(request):
    courses = Course.objects.filter(difficulty='advanced')
    context = {
        'courses': courses,
        'difficulty': 'advanced'
    }
    return render(request, 'advanced_course.html', context)

def video_tutorials(request):
    return render(request, 'video_tutorials.html')

def code_examples(request):
    return render(request, 'code_examples.html')

def practice_exercises(request):
    return render(request, 'practice_exercises.html')

@ensure_csrf_cookie
def registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'registration.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'registration.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'A user with this email already exists.')
            return render(request, 'registration.html')
        
        # Create new user
        try:
            user = User.objects.create(
                firstname=first_name,
                lastname=last_name,
                email=email
            )
            user.set_password(password)
            user.save()
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'An error occurred during registration. Please try again.')
            return render(request, 'registration.html')
    
    return render(request, 'registration.html')
    
@ensure_csrf_cookie
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'login.html')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                # Store user info in session
                request.session['user_id'] = user.id
                request.session['user_name'] = f"{user.firstname} {user.lastname}"
                request.session['user_email'] = user.email
                
                messages.success(request, f'Welcome back, {user.firstname}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'login.html')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return render(request, 'login.html')
    
    return render(request, 'login.html')

def logout(request):
    # Clear session data
    request.session.flush()
    return redirect('home')

# New enrollment and learning views
def enroll_course(request, course_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    course = get_object_or_404(Course, id=course_id)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=user, course=course).exists():
        return redirect('course_detail', course_id=course_id)
    
    # Create enrollment
    enrollment = Enrollment.objects.create(user=user, course=course)
    
    # Initialize lesson progress for all lessons in the course
    for module in course.modules.all():
        for lesson in module.lessons.all():
            LessonProgress.objects.create(user=user, lesson=lesson)
    
    return redirect('course_detail', course_id=course_id)

def course_detail(request, course_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
        is_enrolled = True
    except Enrollment.DoesNotExist:
        enrollment = None
        is_enrolled = False
    
    # Get progress data
    if is_enrolled:
        total_lessons = course.get_total_lessons()
        completed_lessons = LessonProgress.objects.filter(
            user=user, 
            lesson__module__course=course, 
            is_completed=True
        ).count()
        progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
    else:
        progress_percentage = 0
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'progress_percentage': progress_percentage,
        'modules': course.modules.all()
    }
    
    return render(request, 'course_detail.html', context)

def lesson_detail(request, course_id, lesson_id):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    
    # Check if user is enrolled
    try:
        enrollment = Enrollment.objects.get(user=user, course=course)
    except Enrollment.DoesNotExist:
        return redirect('course_detail', course_id=course_id)
    
    # Get or create lesson progress
    progress, created = LessonProgress.objects.get_or_create(
        user=user, 
        lesson=lesson,
        defaults={'progress_percentage': 0}
    )
    
    # Get navigation data
    all_lessons = []
    for module in course.modules.all():
        for lesson_item in module.lessons.all():
            all_lessons.append(lesson_item)
    
    current_index = None
    for i, lesson_item in enumerate(all_lessons):
        if lesson_item.id == lesson.id:
            current_index = i
            break
    
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None
    
    context = {
        'course': course,
        'lesson': lesson,
        'progress': progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'current_index': current_index,
        'total_lessons': len(all_lessons)
    }
    
    return render(request, 'lesson_detail.html', context)

def update_lesson_progress(request, lesson_id):
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.session['user_id'])
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        progress_percentage = int(request.POST.get('progress_percentage', 0))
        is_completed = request.POST.get('is_completed', 'false').lower() == 'true'
        
        progress, created = LessonProgress.objects.get_or_create(
            user=user, 
            lesson=lesson,
            defaults={'progress_percentage': 0}
        )
        
        progress.progress_percentage = progress_percentage
        if is_completed and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
        
        progress.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    
    # Get user's enrollments
    enrollments = Enrollment.objects.filter(user=user, is_active=True)
    
    # Calculate overall progress
    total_courses = enrollments.count()
    completed_courses = enrollments.filter(completed_at__isnull=False).count()
    
    # Get recent activity
    recent_progress = LessonProgress.objects.filter(
        user=user, 
        is_completed=True
    ).order_by('-completed_at')[:5]
    
    context = {
        'user': user,
        'enrollments': enrollments,
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'recent_progress': recent_progress
    }
    
    return render(request, 'dashboard.html', context)

def my_courses(request):
    if 'user_id' not in request.session:
        return redirect('login')
    
    user = get_object_or_404(User, id=request.session['user_id'])
    enrollments = Enrollment.objects.filter(user=user, is_active=True)
    
    context = {
        'enrollments': enrollments
    }
    
    return render(request, 'my_courses.html', context)

# Social Authentication Views

def google_auth(request):
    """Initiate Google OAuth2 authentication"""
    if not settings.GOOGLE_OAUTH2_CLIENT_ID:
        messages.warning(request, 'Google OAuth is not configured. Please contact the administrator.')
        return redirect('login')
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Build authorization URL
    params = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI,
        'scope': 'email profile',
        'response_type': 'code',
        'state': state,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    
    auth_url = f"{settings.GOOGLE_OAUTH2_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

def google_callback(request):
    """Handle Google OAuth2 callback"""
    if not settings.GOOGLE_OAUTH2_CLIENT_ID:
        messages.error(request, 'Google OAuth is not configured.')
        return redirect('login')
    
    # Verify state parameter
    state = request.GET.get('state')
    if state != request.session.get('oauth_state'):
        messages.error(request, 'Invalid OAuth state parameter.')
        return redirect('login')
    
    # Get authorization code
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Authorization code not received.')
        return redirect('login')
    
    # Exchange code for access token
    token_data = {
        'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.GOOGLE_OAUTH2_REDIRECT_URI
    }
    
    try:
        response = requests.post(settings.GOOGLE_OAUTH2_TOKEN_URL, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Get user info
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get(settings.GOOGLE_OAUTH2_USERINFO_URL, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Create or get user
        email = user_info.get('email')
        if not email:
            messages.error(request, 'Email not provided by Google.')
            return redirect('login')
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'firstname': user_info.get('given_name', ''),
                'lastname': user_info.get('family_name', ''),
            }
        )
        
        # Update user info if not created
        if not created:
            user.firstname = user_info.get('given_name', user.firstname)
            user.lastname = user_info.get('family_name', user.lastname)
            user.save()
        
        # Store user info in session
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.firstname} {user.lastname}"
        request.session['user_email'] = user.email
        
        messages.success(request, f'Welcome back, {user.firstname}!')
        return redirect('dashboard')
        
    except requests.RequestException as e:
        messages.error(request, f'Error during Google authentication: {str(e)}')
        return redirect('login')

def github_auth(request):
    """Initiate GitHub OAuth2 authentication"""
    if not settings.GITHUB_OAUTH2_CLIENT_ID:
        messages.warning(request, 'GitHub OAuth is not configured. Please contact the administrator.')
        return redirect('login')
    
    # Generate state parameter for security
    state = secrets.token_urlsafe(32)
    request.session['oauth_state'] = state
    
    # Build authorization URL
    params = {
        'client_id': settings.GITHUB_OAUTH2_CLIENT_ID,
        'redirect_uri': settings.GITHUB_OAUTH2_REDIRECT_URI,
        'scope': 'user:email',
        'state': state
    }
    
    auth_url = f"{settings.GITHUB_OAUTH2_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

def github_callback(request):
    """Handle GitHub OAuth2 callback"""
    if not settings.GITHUB_OAUTH2_CLIENT_ID:
        messages.error(request, 'GitHub OAuth is not configured.')
        return redirect('login')
    
    # Verify state parameter
    state = request.GET.get('state')
    if state != request.session.get('oauth_state'):
        messages.error(request, 'Invalid OAuth state parameter.')
        return redirect('login')
    
    # Get authorization code
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Authorization code not received.')
        return redirect('login')
    
    # Exchange code for access token
    token_data = {
        'client_id': settings.GITHUB_OAUTH2_CLIENT_ID,
        'client_secret': settings.GITHUB_OAUTH2_CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.GITHUB_OAUTH2_REDIRECT_URI
    }
    
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.post(settings.GITHUB_OAUTH2_TOKEN_URL, data=token_data, headers=headers)
        response.raise_for_status()
        token_info = response.json()
        
        if 'access_token' not in token_info:
            messages.error(request, 'Access token not received from GitHub.')
            return redirect('login')
        
        # Get user info
        headers = {
            'Authorization': f"token {token_info['access_token']}",
            'Accept': 'application/vnd.github.v3+json'
        }
        user_response = requests.get(settings.GITHUB_OAUTH2_USERINFO_URL, headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Get user email
        email_response = requests.get('https://api.github.com/user/emails', headers=headers)
        email_response.raise_for_status()
        emails = email_response.json()
        
        # Find primary email
        primary_email = None
        for email_data in emails:
            if email_data.get('primary') and email_data.get('verified'):
                primary_email = email_data.get('email')
                break
        
        if not primary_email:
            messages.error(request, 'No verified email found for GitHub account.')
            return redirect('login')
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=primary_email,
            defaults={
                'firstname': user_info.get('name', '').split()[0] if user_info.get('name') else '',
                'lastname': ' '.join(user_info.get('name', '').split()[1:]) if user_info.get('name') and len(user_info.get('name', '').split()) > 1 else '',
            }
        )
        
        # Update user info if not created
        if not created:
            name_parts = user_info.get('name', '').split()
            if len(name_parts) > 0:
                user.firstname = name_parts[0]
                user.lastname = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                user.save()
        
        # Store user info in session
        request.session['user_id'] = user.id
        request.session['user_name'] = f"{user.firstname} {user.lastname}"
        request.session['user_email'] = user.email
        
        messages.success(request, f'Welcome back, {user.firstname}!')
        return redirect('dashboard')
        
    except requests.RequestException as e:
        messages.error(request, f'Error during GitHub authentication: {str(e)}')
        return redirect('login')