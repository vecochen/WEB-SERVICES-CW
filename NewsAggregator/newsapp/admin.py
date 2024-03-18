from django.contrib import admin
from .models import Author, NewsStory

# Register your models here.
admin.site.register(Author)
admin.site.register(NewsStory)
