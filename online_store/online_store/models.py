from django.db import models

class Book(models.Model):
    app_label = 'online_store' 
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, blank=True) 
    pageCount = models.IntegerField(null=True, blank=True) 
    publishedDate = models.DateTimeField(null=True, blank=True) 
    thumbnailUrl = models.URLField(max_length=200, blank=True)
    shortDescription = models.TextField(blank=True)
    longDescription = models.TextField(blank=True)
    status = models.CharField(max_length=20, blank=True)
    authors = models.CharField(max_length=255, blank=True)  
    categories = models.CharField(max_length=255, blank=True)  

    def __str__(self):
        return self.title
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Author(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name