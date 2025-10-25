# courses/models.py

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class Course(models.Model):
    """
    Main Course model - created by Chefs
    Contains all information about a course including pricing, level, and content
    """
    LEVEL_CHOICES = (
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    )
    
    chef = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='courses', 
        limit_choices_to={'role': 'CHEF'},
        help_text="Chef who created this course"
    )
    title = models.CharField(max_length=200, help_text="Course title")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL-friendly version of title")
    description = models.TextField(help_text="Detailed course description")
    short_description = models.CharField(
        max_length=300, 
        help_text="Brief description for course card (max 300 characters)"
    )
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/', 
        blank=True, 
        null=True,
        help_text="Course cover image"
    )
    
    # Pricing and Course Details
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Course price in USD"
    )
    level = models.CharField(
        max_length=15, 
        choices=LEVEL_CHOICES, 
        default='BEGINNER',
        help_text="Difficulty level"
    )
    duration_hours = models.PositiveIntegerField(
        help_text="Estimated course duration in hours"
    )
    
    # Publishing
    is_published = models.BooleanField(
        default=False,
        help_text="Make course visible to students"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_published']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            # Ensure slug is unique
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_enrolled_count(self):
        """Get number of paid enrollments"""
        return self.enrollments.filter(is_paid=True).count()
    
    def get_total_revenue(self):
        """Calculate total revenue from this course"""
        return self.enrollments.filter(is_paid=True).aggregate(
            total=models.Sum('amount_paid')
        )['total'] or 0
    
    def get_total_duration_minutes(self):
        """Calculate total duration of all classes in minutes"""
        return self.classes.aggregate(
            total=models.Sum('duration_minutes')
        )['total'] or 0


class Class(models.Model):
    """
    Individual classes/lessons within a course
    Each class represents a single lesson or module
    """
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='classes',
        help_text="Course this lesson belongs to"
    )
    title = models.CharField(max_length=200, help_text="Lesson title")
    description = models.TextField(help_text="Lesson description")
    order = models.PositiveIntegerField(
        default=0, 
        help_text="Order of lesson in course (1, 2, 3, etc.)"
    )
    
    # Video Content
    video_url = models.URLField(
        blank=True, 
        null=True, 
        help_text="YouTube, Vimeo, or other video platform URL"
    )
    duration_minutes = models.PositiveIntegerField(
        help_text="Lesson duration in minutes"
    )
    
    # Optional Materials
    notes = models.TextField(
        blank=True, 
        null=True, 
        help_text="Lesson notes, transcript, or additional information"
    )
    attachments = models.FileField(
        upload_to='courses/class_materials/', 
        blank=True, 
        null=True,
        help_text="PDF, documents, or other downloadable resources"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Class'
        verbose_name_plural = 'Classes'
        indexes = [
            models.Index(fields=['course', 'order']),
        ]
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_next_class(self):
        """Get the next class in the course"""
        return Class.objects.filter(
            course=self.course,
            order__gt=self.order
        ).order_by('order').first()
    
    def get_previous_class(self):
        """Get the previous class in the course"""
        return Class.objects.filter(
            course=self.course,
            order__lt=self.order
        ).order_by('-order').first()


class Recipe(models.Model):
    """
    Recipes shared by chefs, can be linked to courses or standalone
    """
    DIFFICULTY_CHOICES = (
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    )
    
    chef = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='recipes', 
        limit_choices_to={'role': 'CHEF'},
        help_text="Chef who created this recipe"
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='recipes', 
        help_text="Link to a course (optional)"
    )
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Recipe name")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(help_text="Brief description of the dish")
    
    # Recipe Content
    ingredients = models.TextField(
        help_text="List all ingredients (one per line or separated by commas)"
    )
    instructions = models.TextField(
        help_text="Step-by-step cooking instructions"
    )
    
    # Timing and Details
    prep_time_minutes = models.PositiveIntegerField(
        help_text="Preparation time in minutes"
    )
    cook_time_minutes = models.PositiveIntegerField(
        help_text="Cooking time in minutes"
    )
    servings = models.PositiveIntegerField(
        default=4,
        help_text="Number of servings"
    )
    difficulty = models.CharField(
        max_length=10, 
        choices=DIFFICULTY_CHOICES, 
        default='MEDIUM',
        help_text="Recipe difficulty level"
    )
    
    # Media
    image = models.ImageField(
        upload_to='recipes/', 
        blank=True, 
        null=True,
        help_text="Photo of the finished dish"
    )
    
    # Publishing
    is_public = models.BooleanField(
        default=True, 
        help_text="Make recipe publicly visible or course-exclusive"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_public']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def total_time(self):
        """Calculate total time (prep + cook)"""
        return self.prep_time_minutes + self.cook_time_minutes
    
    def get_ingredients_list(self):
        """Return ingredients as a list"""
        return [ing.strip() for ing in self.ingredients.split('\n') if ing.strip()]
    
    def get_instructions_list(self):
        """Return instructions as a list of steps"""
        return [inst.strip() for inst in self.instructions.split('\n') if inst.strip()]


class Book(models.Model):
    """
    E-books or reference materials by chefs
    Can be linked to courses or offered as standalone resources
    """
    chef = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='books', 
        limit_choices_to={'role': 'CHEF'},
        help_text="Chef who uploaded this book"
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='books', 
        help_text="Link to a course (optional)"
    )
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Book title")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(help_text="Book description or synopsis")
    author = models.CharField(max_length=200, help_text="Author name(s)")
    
    # Media Files
    cover_image = models.ImageField(
        upload_to='books/covers/', 
        blank=True, 
        null=True,
        help_text="Book cover image"
    )
    pdf_file = models.FileField(
        upload_to='books/pdfs/', 
        blank=True, 
        null=True,
        help_text="PDF file of the book"
    )
    external_link = models.URLField(
        blank=True, 
        null=True, 
        help_text="External link to book (Amazon, publisher website, etc.)"
    )
    
    # Book Details
    pages = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text="Number of pages"
    )
    isbn = models.CharField(
        max_length=13, 
        blank=True, 
        null=True,
        help_text="ISBN-10 or ISBN-13"
    )
    publication_year = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Year of publication"
    )
    language = models.CharField(
        max_length=50,
        default='English',
        help_text="Book language"
    )
    
    # Publishing
    is_public = models.BooleanField(
        default=True, 
        help_text="Make book publicly visible or course-exclusive"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Book'
        verbose_name_plural = 'Books'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_public']),
        ]
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def has_downloadable_file(self):
        """Check if book has a downloadable PDF"""
        return bool(self.pdf_file)


class Enrollment(models.Model):
    """
    Tracks student enrollments and purchases
    Links students to courses with payment information
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='enrollments', 
        limit_choices_to={'role': 'STUDENT'},
        help_text="Student enrolled in the course"
    )
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        related_name='enrollments',
        help_text="Course the student is enrolled in"
    )
    
    # Payment Information
    is_paid = models.BooleanField(
        default=False,
        help_text="Whether payment has been completed"
    )
    payment_id = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        help_text="Stripe payment intent ID or transaction reference"
    )
    amount_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text="Amount paid for this enrollment"
    )
    payment_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time of payment"
    )
    
    # Progress Tracking
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Course completion percentage (0-100)"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Whether the course has been completed"
    )
    last_accessed = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Last time student accessed the course"
    )
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="Date when course was completed"
    )
    
    class Meta:
        ordering = ['-enrolled_at']
        unique_together = ['student', 'course']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        indexes = [
            models.Index(fields=['student', 'is_paid']),
            models.Index(fields=['course', 'is_paid']),
            models.Index(fields=['-enrolled_at']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def mark_as_completed(self):
        """Mark enrollment as completed"""
        from django.utils import timezone
        self.completed = True
        self.progress_percentage = 100
        self.completed_at = timezone.now()
        self.save()
    
    def update_progress(self):
        """Calculate and update progress based on completed classes"""
        # This would be expanded with a ClassProgress model
        # For now, it's a placeholder
        total_classes = self.course.classes.count()
        if total_classes > 0:
            # Logic to count completed classes would go here
            pass
    
    def get_days_enrolled(self):
        """Get number of days since enrollment"""
        from django.utils import timezone
        delta = timezone.now() - self.enrolled_at
        return delta.days


class ClassProgress(models.Model):
    """
    Tracks individual class completion for each student
    Optional model for detailed progress tracking
    """
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='class_progress',
        help_text="Related enrollment"
    )
    lesson = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='student_progress',
        help_text="Class/Lesson being tracked"
    )
    
    # Progress
    is_completed = models.BooleanField(
        default=False,
        help_text="Whether student has completed this lesson"
    )
    time_spent_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Time spent on this lesson in minutes"
    )
    last_position_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Last video position in seconds (for resume)"
    )
    
    # Timestamps
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When student first accessed this lesson"
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When student completed this lesson"
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        help_text="Last time student accessed this lesson"
    )
    
    class Meta:
        ordering = ['lesson__order']
        unique_together = ['enrollment', 'lesson']
        verbose_name = 'Class Progress'
        verbose_name_plural = 'Class Progress'
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title}"
    
    def mark_as_completed(self):
        """Mark this lesson as completed"""
        from django.utils import timezone
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()
        
        # Update overall enrollment progress
        self.enrollment.update_progress()


class Review(models.Model):
    """
    Course reviews and ratings by students
    Optional model for student feedback
    """
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="Course being reviewed"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        limit_choices_to={'role': 'STUDENT'},
        help_text="Student who wrote the review"
    )
    
    # Rating and Review
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    title = models.CharField(
        max_length=200,
        help_text="Review title"
    )
    comment = models.TextField(
        help_text="Detailed review comment"
    )
    
    # Moderation
    is_approved = models.BooleanField(
        default=True,
        help_text="Whether review is approved for display"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['course', 'student']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating}★)"