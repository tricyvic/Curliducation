from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role-based access
    Roles: CHEF or STUDENT
    """
    ROLE_CHOICES = (
        ('CHEF', 'Chef'),
        ('STUDENT', 'Student'),
        ('ADMIN', 'Admin'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Chef-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True, 
                                     help_text="e.g., Italian Cuisine, Pastry, etc.")
    years_of_experience = models.PositiveIntegerField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'ADMIN' or self.role == 'CHEF'
    
    def is_chef(self):
        return self.role == 'CHEF'
    
    def is_student(self):
        return self.role == 'STUDENT'
    
    class Meta:
        ordering = ['-created_at']