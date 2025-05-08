import nanoid
from django.contrib import admin
from django.db import models


class Demo(models.Model):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
