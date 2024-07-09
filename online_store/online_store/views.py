from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response

import requests
from iso8601 import parse_date
from django.db.models import Q

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly] 

    def get_queryset(self):
        return Book.objects.all()

    def list(self, request):
        json_url = 'https://gitlab.grokhotov.ru/hr/python-test-vacancy/-/raw/master/books.json?inline=false'
        response = requests.get(json_url)

        if response.status_code == 200:
            data = response.json()

            for book_data in data:
                published_date_str = book_data.get('publishedDate', {}).get('$date')
                if published_date_str:
                    published_date = parse_date(published_date_str)
                    book_data['publishedDate'] = published_date
                else:
                    book_data['publishedDate'] = None

                title = book_data.get('title')
                author = book_data.get('authors')

                if title and author:
                    if Book.objects.filter(title=title, authors=author).exists():
                        continue  

                book = Book.objects.create(**book_data)

            serializer = BookSerializer(self.get_queryset(), many=True) 
            return Response(serializer.data)
        
    @action(detail=False, methods=['get'], url_path='category/(?P<category>\w+)')
    def get_by_category(self, request, category):
        """Получение книг по категории"""
        books = Book.objects.filter(Q(categories__icontains=category))
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='categories/(?P<level>\d+)')
    def get_nested_categories(self, request, level):
        """Получение категорий заданного уровня и последующего"""
        books = self.get_queryset()
        categories_data = []
        level = int(level)
        for book in books:
            categories_list = book.categories.strip('[]').split(', ')  # Убираем скобки и разделяем по запятой
            categories_data.append([c.strip("\'\'") for c in categories_list[ :level+2 ]]) # Убираем лишние пробелы
        return Response(categories_data)
    
    @action(detail=False, methods=['get'], url_path='(?P<title>\w+)')
    def get_certain_book(self, request, title):
        """Получение определённой книги"""
        books = Book.objects.filter(Q(title__icontains=title))
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
