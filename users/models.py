from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image, ImageEnhance
import os

def validate_image(image):
    """Validate the uploaded image size and dimensions."""
    try:
        # Check file size (5MB limit)
        if image.size > 5 * 1024 * 1024:
            raise ValidationError('Profile picture must be less than 5MB')

        # Validate image dimensions
        img = Image.open(image)
        if img.width > 800 or img.height > 800:
            raise ValidationError('Profile picture dimensions must be 800x800 or smaller')
            
    except Exception as e:
        raise ValidationError(f"Error processing image: {str(e)}")

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('analyst', 'Data Analyst'),
        ('marketer', 'Marketer'),
        ('researcher', 'Researcher'),
        ('general_user', 'General User'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('IT', 'Information Technology'),
        ('Marketing', 'Marketing'),
        ('Research', 'Research'),
        ('General', 'General'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='general_user')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='General')
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']), validate_image],
        help_text="Upload a profile picture (JPG, JPEG, or PNG). Maximum size: 5MB, dimensions: 800x800 or smaller."
    )
    bio = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_analyst(self):
        return self.role == 'analyst'

    @property
    def is_marketer(self):
        return self.role == 'marketer'

    @property
    def is_researcher(self):
        return self.role == 'researcher'

    def save(self, *args, **kwargs):
        if self.profile_picture:
            # Resize the image to a reasonable size
            img = Image.open(self.profile_picture)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)
        super().save(*args, **kwargs)

class Report(models.Model):
    TYPE_CHOICES = [
        ('analysis', 'Data Analysis'),
        ('marketing', 'Marketing Report'),
        ('research', 'Research Report'),
        ('system', 'System Report'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.author.username}"

class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    TYPE_CHOICES = [
        ('email', 'Email Campaign'),
        ('social', 'Social Media Campaign'),
        ('survey', 'Survey Campaign'),
        ('promotion', 'Promotional Campaign')
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    target_audience = models.TextField(blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    success_metrics = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def is_active(self):
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date

    def is_completed(self):
        return self.status == 'completed' or (self.end_date < timezone.now() and self.status == 'active')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()