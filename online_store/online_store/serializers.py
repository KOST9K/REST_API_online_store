from rest_framework import serializers
from .models import Book
from .models import Category

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        # fields = ['title', 'isbn', 'pageCount', 'publishedDate', 'thumbnailUrl', 'shortDescription', 'longDescription', 'status']
        exclude = ['id']
    
    # title = serializers.CharField()
    # isbn = serializers.CharField()
    # pageCount = serializers.IntegerField()
    # publishedDate = serializers.DateTimeField()
    # thumbnailUrl = serializers.URLField()
    # shortDescription = serializers.CharField(allow_blank=True)
    # longDescription = serializers.CharField(allow_blank=True)
    # status = serializers.CharField()
    # authors = serializers.ListField(child=serializers.CharField(max_length=200))
    # categories = serializers.ListField(child=serializers.CharField(max_length=200))

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
