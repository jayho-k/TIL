from csv import list_dialects
from django.contrib import admin
from .models import Article

# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('pk','title','content','create_at','updeate_at',)


admin.site.register(Article, ArticleAdmin)