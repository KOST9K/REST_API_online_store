from django.db import models
from django.db.models import UniqueConstraint
from phonenumber_field.modelfields import PhoneNumberField

class Author(models.Model):
    name = models.CharField(max_length=255)
    # class Meta:
    #          constraints = [
    #              UniqueConstraint(fields=['name'], name='unique_author_name')
    #          ]
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)
    # class Meta:
    #          constraints = [
    #              UniqueConstraint(fields=['name'], name='unique_category_name')
    #          ]
    def __str__(self):
        return self.name

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
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.title
    
class Feedback(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255)
    commentary = models.TextField()
    # phone = PhoneNumberField(blank=True)
    phone = models.CharField(max_length=255)

    def __str__(self):
        return self.name


