# courses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ============================================
    # PUBLIC VIEWS
    # ============================================
    
    # Homepage
    path('', views.home, name='home'),
    
    # Course Browsing (Public)
    path('courses/', views.course_list, name='course_list'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    
    # Recipe Browsing (Public)
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<slug:slug>/', views.recipe_list, name='recipe_detail'),
    
    # Book Browsing (Public)
    path('books/', views.book_list, name='book_list'),
    path('books/<slug:slug>/', views.book_list, name='book_detail'),
    
    # ============================================
    # CHEF DASHBOARD & MANAGEMENT
    # ============================================
    
    # Dashboard
    path('chef/dashboard/', views.chef_dashboard, name='chef_dashboard'),
    
    # Course Management
    path('chef/courses/', views.chef_courses, name='chef_courses'),
    path('chef/course/create/', views.course_create, name='course_create'),
    path('chef/course/<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('chef/course/<slug:slug>/delete/', views.course_delete, name='course_delete'),
    # path('chef/course/<slug:slug>/toggle-publish/', views.course_toggle_publish, name='course_toggle_publish'),
    
    # Class/Lesson Management
    path('chef/course/<slug:course_slug>/class/create/', views.class_create, name='class_create'),
    path('chef/class/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('chef/class/<int:pk>/delete/', views.class_delete, name='class_delete'),
    
    # # Recipe Management (Chef)
    # path('chef/recipes/', views.chef_recipes, name='chef_recipes'),
    # path('chef/recipe/create/', views.recipe_create, name='recipe_create'),
    # path('chef/recipe/<slug:slug>/edit/', views.recipe_edit, name='recipe_edit'),
    # path('chef/recipe/<slug:slug>/delete/', views.recipe_delete, name='recipe_delete'),
    
    # Book Management (Chef)
    # path('chef/books/', views.chef_books, name='chef_books'),
    # path('chef/book/create/', views.book_create, name='book_create'),
    # path('chef/book/<slug:slug>/edit/', views.book_edit, name='book_edit'),
    # path('chef/book/<slug:slug>/delete/', views.book_delete, name='book_delete'),
    
    # ============================================
    # STUDENT VIEWS
    # ============================================
    
    # My Courses (Student Dashboard)
    path('my-courses/', views.my_courses, name='my_courses'),
    path('my-courses/<slug:slug>/', views.course_detail, name='my_course_detail'),
    
    # Course Enrollment & Payment
    # path('course/<slug:slug>/enroll/', views.c, name='course_enroll'),
    # path('course/<slug:slug>/checkout/', views.course_checkout, name='course_checkout'),
    
    # Progress Tracking
    # path('course/<slug:course_slug>/class/<int:class_id>/complete/', views.mark_class_complete, name='mark_class_complete'),
    
    # ============================================
    # SEARCH & FILTER
    # ============================================
    
    # path('search/', views.search, name='search'),
    # path('courses/category/<str:category>/', views.course_by_category, name='course_by_category'),
    
    # # ============================================
    # # REVIEWS (Optional - for Day 3)
    # # ============================================
    
    # path('course/<slug:slug>/review/', views.add_review, name='add_review'),
    # path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
    # path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),
]