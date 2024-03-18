from django.db import models
from django.contrib.auth.models import User
    
class Author(models.Model):
    name = models.CharField(max_length = 100)
    username = models.CharField(max_length = 64, unique = True)
    password = models.CharField(max_length = 64)
    login_token = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name # Returns name when Author instance is called
    
    
class NewsStory(models.Model):
    headline = models.CharField(max_length = 64)

    categoryChoices = [
        ('pol', 'Politics'),
        ('art', 'Art'),
        ('tech', 'Technology'),
        ('trivia', 'Trivia'),
    ]
    category = models.CharField(max_length = 10, choices = categoryChoices)
    
    regionChoices = [
        ('uk', 'United Kingdom'),
        ('eu', 'Europe'),
        ('w', 'World'),
    ]
    region = models.CharField(max_length = 10, choices = regionChoices)
    author = models.ForeignKey(Author, on_delete=models.CASCADE) # Linked to authors table
    date = models.DateField()
    details = models.CharField(max_length = 128)
    
    def __str__(self):
        return self.headline
    


    

