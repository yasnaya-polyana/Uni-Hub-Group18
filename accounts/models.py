from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator

# Create your models here.

# Course Types
#
#
class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.TextField(max_length=100)

    def __str__(self):
        return self.course_name

# Student Account Creation 
#
#
class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    student_id = models.CharField(max_length=8, validators=[MinLengthValidator(8), MaxLengthValidator(8)], unique=True, null=True, blank=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username