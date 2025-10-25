# courses/forms.py

from django import forms
from .models import Course, Class, Recipe, Book

class CourseForm(forms.ModelForm):
    """
    Form for creating and updating courses
    """
    class Meta:
        model = Course
        fields = ['title', 'short_description', 'description', 'thumbnail', 
                  'price', 'level', 'duration_hours', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course title'
            }),
            'short_description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description (max 300 characters)',
                'maxlength': '300'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed course description'
            }),
            'thumbnail': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Estimated hours'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text
        self.fields['is_published'].help_text = 'Check to make this course visible to students'


class ClassForm(forms.ModelForm):
    """
    Form for creating and updating classes/lessons
    """
    class Meta:
        model = Class
        fields = ['title', 'description', 'order', 'video_url', 
                  'duration_minutes', 'notes', 'attachments']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lesson title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lesson description'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Order in course'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube or Vimeo URL'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Duration in minutes'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Lesson notes or transcript (optional)'
            }),
            'attachments': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class RecipeForm(forms.ModelForm):
    """
    Form for creating and updating recipes
    """
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'course', 'ingredients', 'instructions',
                  'prep_time_minutes', 'cook_time_minutes', 'servings', 
                  'difficulty', 'image', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Recipe title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description'
            }),
            'course': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ingredients': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'List ingredients (one per line)'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Step-by-step instructions'
            }),
            'prep_time_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'cook_time_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'servings': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-select'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter courses to show only chef's own courses
        self.fields['course'].queryset = Course.objects.filter(chef=user)
        self.fields['course'].required = False


class BookForm(forms.ModelForm):
    """
    Form for creating and updating books
    """
    class Meta:
        model = Book
        fields = ['title', 'description', 'author', 'course', 'cover_image',
                  'pdf_file', 'external_link', 'pages', 'isbn', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Book description'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author name(s)'
            }),
            'course': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'pdf_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'external_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'External link (optional)'
            }),
            'pages': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'isbn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ISBN (optional)'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter courses to show only chef's own courses
        self.fields['course'].queryset = Course.objects.filter(chef=user)
        self.fields['course'].required = False