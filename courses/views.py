from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from accounts.models import User
from .models import Course, Class, Recipe, Book, Enrollment
from .forms import CourseForm, ClassForm, RecipeForm, BookForm

# ============================================
# PUBLIC VIEWS
# ============================================

def home(request):
    featured_courses = Course.objects.filter(is_published=True)[:6]
    
    context = {
        'featured_courses': featured_courses,
        'total_courses': Course.objects.filter(is_published=True).count(),
        'total_students': User.objects.filter(role='STUDENT').count(),
        'total_chefs': User.objects.filter(role='CHEF').count(),
        'total_recipes': Recipe.objects.filter(is_public=True).count(),
    }
    return render(request, 'courses/home.html', context)



# ============================================
# STUDENT VIEWS
# ============================================

@login_required
def my_courses(request):
    """Student's enrolled courses"""
    if request.user.is_chef():
        return redirect('chef_dashboard')
    
    enrollments = Enrollment.objects.filter(
        student=request.user,
        is_paid=True
    ).select_related('course')
    
    context = {'enrollments': enrollments}
    return render(request, 'courses/my_courses.html', context) 


def course_list(request):
    """List all published courses"""
    courses = Course.objects.filter(is_published=True).select_related('chef')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(chef__username__icontains=query)
        )
    
    # Filter by level
    level = request.GET.get('level')
    if level:
        courses = courses.filter(level=level)
    
    context = {
        'courses': courses,
        'query': query,
        'selected_level': level
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    """Course detail view"""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    classes = course.classes.all()
    recipes = course.recipes.filter(is_public=True)
    books = course.books.filter(is_public=True)
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            is_paid=True
        ).exists()
    
    context = {
        'course': course,
        'classes': classes,
        'recipes': recipes,
        'books': books,
        'is_enrolled': is_enrolled
    }
    return render(request, 'courses/course_detail.html', context)


def recipe_list(request):
    """List all public recipes"""
    recipes = Recipe.objects.filter(is_public=True).select_related('chef')
    context = {'recipes': recipes}
    return render(request, 'courses/recipe_list.html', context)


def book_list(request):
    """List all public books"""
    books = Book.objects.filter(is_public=True).select_related('chef')
    context = {'books': books}
    return render(request, 'courses/book_list.html', context)


# ============================================
# CHEF DASHBOARD
# ============================================

@login_required
def chef_dashboard(request):
    """Chef dashboard - main control panel"""
    if not request.user.is_chef():
        messages.error(request, 'Access denied. Chef account required.')
        return redirect('home')
    
    courses = Course.objects.filter(chef=request.user)
    recipes = Recipe.objects.filter(chef=request.user)
    books = Book.objects.filter(chef=request.user)
    
    # Stats
    total_courses = courses.count()
    published_courses = courses.filter(is_published=True).count()
    total_students = Enrollment.objects.filter(
        course__chef=request.user,
        is_paid=True
    ).values('student').distinct().count()
    
    context = {
        'courses': courses[:5],  # Latest 5
        'recipes': recipes[:5],
        'books': books[:5],
        'total_courses': total_courses,
        'published_courses': published_courses,
        'total_students': total_students,
    }
    return render(request, 'courses/chef_dashboard.html', context)


# ============================================
# COURSE CRUD (Chef Only)
# ============================================

@login_required
def chef_courses(request):
    """List all chef's courses"""
    if not request.user.is_chef():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    courses = Course.objects.filter(chef=request.user)
    context = {'courses': courses}
    return render(request, 'courses/chef_courses.html', context)


@login_required
def course_create(request):
    """Create new course"""
    if not request.user.is_chef():
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.chef = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('course_edit', slug=course.slug)
    else:
        form = CourseForm()
    
    context = {'form': form, 'action': 'Create'}
    return render(request, 'courses/course_form.html', context)


@login_required
def course_edit(request, slug):
    """Edit existing course"""
    course = get_object_or_404(Course, slug=slug, chef=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_edit', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    
    # Get classes for this course
    classes = course.classes.all()
    
    context = {
        'form': form,
        'course': course,
        'classes': classes,
        'action': 'Edit'
    }
    return render(request, 'courses/course_form.html', context)


@login_required
def course_delete(request, slug):
    """Delete course"""
    course = get_object_or_404(Course, slug=slug, chef=request.user)
    
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f'Course "{course_title}" deleted successfully!')
        return redirect('chef_courses')
    
    context = {'course': course}
    return render(request, 'courses/course_confirm_delete.html', context)


# ============================================
# CLASS CRUD (Chef Only)
# ============================================

@login_required
def class_create(request, course_slug):
    """Add class to course"""
    course = get_object_or_404(Course, slug=course_slug, chef=request.user)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES)
        if form.is_valid():
            new_class = form.save(commit=False)
            new_class.course = course
            new_class.save()
            messages.success(request, f'Class "{new_class.title}" added successfully!')
            return redirect('course_edit', slug=course.slug)
    else:
        form = ClassForm()
    
    context = {'form': form, 'course': course, 'action': 'Add'}
    return render(request, 'courses/class_form.html', context)


@login_required
def class_edit(request, pk):
    """Edit class"""
    class_obj = get_object_or_404(Class, pk=pk, course__chef=request.user)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, request.FILES, instance=class_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('course_edit', slug=class_obj.course.slug)
    else:
        form = ClassForm(instance=class_obj)
    
    context = {'form': form, 'class': class_obj, 'action': 'Edit'}
    return render(request, 'courses/class_form.html', context)


@login_required
def class_delete(request, pk):
    """Delete class"""
    class_obj = get_object_or_404(Class, pk=pk, course__chef=request.user)
    course_slug = class_obj.course.slug
    
    if request.method == 'POST':
        class_title = class_obj.title
        class_obj.delete()
        messages.success(request, f'Class "{class_title}" deleted successfully!')
        return redirect('course_edit', slug=course_slug)
    
    context = {'class': class_obj}
    return render(request, 'courses/class_confirm_delete.html', context)