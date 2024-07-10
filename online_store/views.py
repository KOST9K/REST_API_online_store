from rest_framework import viewsets, pagination
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

import requests
from iso8601 import parse_date
from django.db.models import Q
from django.shortcuts import render

from .models import Book, Author, Category, Feedback
from .serializers import BookSerializer, AuthorSerializer, CategorySerializer, FeedbackSerializer

# ISBN have symbols instead nums
# Authors have "" and Jr.
# short and long description can have ""
# publishDate can be not exist
# MIchael Barlotta or Michael Barlotta or Michael J. Barlotta in authors
# books duplicates with category and without

class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly] 
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = 5

    def get_queryset(self):
        return Book.objects.all()

    def list(self, request):
        """Recieve all books"""
        json_url = 'https://gitlab.grokhotov.ru/hr/python-test-vacancy/-/raw/master/books.json?inline=false'
        response = requests.get(json_url)

        if response.status_code == 200:
            data = response.json()

            for book_data in data:
                title = book_data.get('title')
                authors_list= book_data.get('authors')
                categories_list = book_data.get('categories')

                if title:
                    # Deeper duplicates filtration, but less effective (books have same author with mistakes in name)
                    # authors = Author.objects.filter(name__in=authors_list)
                    # if Book.objects.filter(title=title, authors__in=authors).exists():
                    if Book.objects.filter(title=title).exists():
                        continue  

                fields_to_remove = ["authors", "categories"]
                for field in fields_to_remove:
                    if field in book_data:
                        del book_data[field]

                if any(author == '' for author in authors_list):
                    authors_list.remove("")
                    
                published_date_str = book_data.get('publishedDate', {}).get('$date')
                if published_date_str:
                    published_date = parse_date(published_date_str)
                    book_data['publishedDate'] = published_date
                else:
                    book_data['publishedDate'] = None

                book = Book.objects.create(**book_data)

                if authors_list:
                    for author_name in authors_list:
                        author, created = Author.objects.get_or_create(name=author_name)
                        book.authors.add(author)

                if categories_list:
                    for category_name in categories_list:
                        category, created = Category.objects.get_or_create(name=category_name)
                        book.categories.add(category)
                else:
                    category = Category.objects.create(name="New")
                    book.categories.add(category)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset) 

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
            
        
    @action(detail=False, methods=['get'], url_path='category/(?P<category>\w+)')
    def get_by_category(self, request, category):
        """Getting books by category"""
        books = Book.objects.filter(categories__name__icontains=category) 
        page = self.paginate_queryset(books)
        if page is not None:
            serializer = BookSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)
    
    # @action(detail=False, methods=['get'], url_path='categories/(?P<level>\d+)')
    # def get_nested_categories(self, request, level):
    
    #     """Recieving current and next deep category"""
    #     level = int(level)
    #     categories = Category.objects.filter(
    #         Q(level__gte=level)  # Фильтруем категории, уровень которых больше или равен заданному
    #     ).distinct('name')  # Извлекаем только уникальные категории

    #     page = self.paginate_queryset(categories)  # Используем пагинацию
    #     if page is not None:
    #         serializer = CategorySerializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)  # Возвращаем пагинированный ответ
    #     else:
    #         serializer = CategorySerializer(categories, many=True)
    #         return Response(serializer.data)  # Возвращаем обычный ответ, если пагинация не требуется
    
    @action(detail=False, methods=['get'], url_path='(?P<title>[^/]+)')
    def get_certain_book(self, request, title):
        """Recieve certain book"""
        print(title)
        books = Book.objects.filter(Q(title__icontains=title))
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class FeedbackForm(APIView):
    def get_queryset(self):
        return Feedback.objects.all()

    def get(self, request):
        return render(request, 'feedback.html')
    
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Спасибо за вашу обратную связь!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
        # feedbacks = self.get_queryset()
        # serializer = FeedbackSerializer(feedbacks, many=True)
        # return Response(serializer.data)

class FeedbackViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Feedback.objects.all()

    @action(detail=False, methods=['get'], url_path='list')
    def get_allfeedback(self, request):
        queryset = Feedback.objects.all()
        serializer_class = FeedbackSerializer(queryset, many=True)
        return Response(serializer_class.data)

class UserLoginView(TokenObtainPairView):
    """
    Обрабатывает авторизацию пользователя, возвращая пары 
    токенов доступа и обновления.
    """
    pass