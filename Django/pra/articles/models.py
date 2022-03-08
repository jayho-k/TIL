from unittest.mock import create_autospec
from django.db import models

# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=10)
    content = models.TextField()
    create_at = models.DateField(auto_now_add=True)
    updeate_at = models.DateField(auto_now=True)

    def __str__(self):
        return f'제목 {self.title}: {self.content}'