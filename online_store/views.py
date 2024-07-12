from rest_framework import viewsets, pagination, status, filters
from rest_framework.decorators import action
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import AllowAny
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.models import User

from iso8601 import parse_date
import requests, time
import django_filters
import os

from .models import Book, Author, Category, Feedback
from .serializers import BookSerializer, AuthorSerializer, CategorySerializer, FeedbackSerializer

def download_image(thumbnail_url, image_path):
        if os.path.exists(image_path):
            print(f"Image already exists at {image_path}. Skipping download.")
            return True

        retries = 3
        delay = 5

        for attempt in range(retries):
            try:
                response = requests.get(thumbnail_url, stream=True, timeout=10)
                response.raise_for_status()
                with open(image_path, 'wb') as image_file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            image_file.write(chunk)
                return True
            except requests.exceptions.RequestException as e:
                print(f"Error while image download: {e}")
                if attempt < retries - 1:
                    print(f"Retry in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise 
        return False

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    author = django_filters.CharFilter(field_name='authors__name', lookup_expr='icontains')
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains')
    publishedDate = django_filters.DateFilter(field_name='publishedDate', lookup_expr='gte')

    class Meta:
        model = Book
        fields = ['title', 'author', 'status', 'publishedDate']


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly] 
    pagination_class = pagination.PageNumberPagination
    pagination_class.page_size = 5
    authentication_classes = [JWTAuthentication]

    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = BookFilter

    

    def get_queryset(self):
        json_url = 'https://gitlab.grokhotov.ru/hr/python-test-vacancy/-/raw/master/books.json?inline=false'
        response = requests.get(json_url)

        if response.status_code == 200:
            data = response.json()

            for book_data in data:
                title = book_data.get('title')
                authors_list = book_data.get('authors')
                categories_list = book_data.get('categories')
                thumbnail = book_data.get('thumbnailUrl')
                if title:
                    # Deeper duplicates filtration, but less effective (books have same author with mistakes in name)
                    # authors = Author.objects.filter(name__in=authors_list)
                    # if Book.objects.filter(title=title, authors__in=authors).exists():
                    if Book.objects.filter(title=title).exists():
                        continue  

                fields_to_remove = ["authors", "categories", "thumbnailUrl"]
                for field in fields_to_remove:
                    if field in book_data:
                        del book_data[field]

                if any(author == '' for author in authors_list):
                    authors_list.remove("")

                if any(category == '' for category in categories_list):
                    categories_list.remove("")
                    
                published_date_str = book_data.get('publishedDate', {}).get('$date')
                if published_date_str:
                    published_date = parse_date(published_date_str)
                    book_data['publishedDate'] = published_date
                else:
                    book_data['publishedDate'] = None

                if thumbnail:
                    filename = os.path.basename(thumbnail)
                    image_path = os.path.join(settings.MEDIA_ROOT, 'book_images', filename)

                    if download_image(thumbnail, image_path):
                        book_data['thumbnail'] = os.path.join('book_images', filename)

                book = Book.objects.create(**book_data)

                if authors_list:
                    for author_name in authors_list:
                        author, created = Author.objects.get_or_create(name=author_name)
                        book.authors.add(author)

                new_category, created = Category.objects.get_or_create(name="New")

                if categories_list:
                    for category_name in categories_list:
                        category, created = Category.objects.get_or_create(name=category_name)
                        book.categories.add(category)
                else:
                    book.categories.add(new_category)

        return Book.objects.all()            
        
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
    
    @action(detail=False, methods=['get'], url_path='categories/(?P<level>\d+)')
    def get_nested_categories(self, request, level):
        """Recieving current and next deep category"""
        level = int(level)
       
        book_categories = []
        books = Book.objects.all()

        for book in books:
            categories_by_book = []
            for category in book.categories.all():
                categories_by_book.append(category) 

            if level < len(categories_by_book):
                current_category = categories_by_book[level]
                next_category = categories_by_book[level + 1] if level + 1 < len(categories_by_book) else None

                book_categories.append({
                    "book_name": book.title,
                    "category_name": CategorySerializer(current_category).data,
                    "children": CategorySerializer(next_category, many=False).data if next_category else None 
                })

        return Response(book_categories)
    
    @action(detail=False, methods=['get'], url_path='(?P<title>[^/]+)')
    def get_certain_book(self, request, title):
        """Recieve certain book and 5 books from the same category"""
        same_category_books_number =5
        book = Book.objects.filter(title=title).first()
        if book:
            category = book.categories.first()
            if category:
                related_books = Book.objects.filter(categories=category).exclude(title=title).order_by('?')[:same_category_books_number]

                serializer = BookSerializer(related_books, many=True)

                related_books_data = serializer.data
                related_books_data.insert(0, BookSerializer(book).data)

                return Response(related_books_data)
            else:
                return Response({"detail": "Book has no category"}, status=400)
        else:
            return Response({"detail": "Book not found"}, status=404)


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


@api_view(['GET', 'POST'])
def login(request):
    """
    Вход в систему и выдача JWT-токенов.
    """
    permission_classes = [AllowAny]
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'detail': 'Пользователь не найден'}, status=status.HTTP_401_UNAUTHORIZED)

    if user.check_password(password):
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        return Response({'refresh': str(refresh), 'access': str(access_token)}, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Неверный пароль'}, status=status.HTTP_401_UNAUTHORIZED)