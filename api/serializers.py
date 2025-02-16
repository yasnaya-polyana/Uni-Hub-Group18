from rest_framework import serializers
from accounts.models import CustomUser, Course

# Course Serializer
#
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_id', 'course_name']

# Simple Custom Serializer
# 
class CustomUserSerializer(serializers.ModelSerializer):
    # Relationship
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'course', 'username', 'email']