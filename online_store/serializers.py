from rest_framework import serializers
from .models import Book, Author, Category, Feedback

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class BookSerializer(serializers.ModelSerializer):
    authors = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    categories = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Book
        fields = '__all__'
        # fields = ['title', 'isbn', 'pageCount', 'publishedDate', 'thumbnailUrl', 'shortDescription', 'longDescription', 'status']
        # exclude = ['id']
    
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

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'