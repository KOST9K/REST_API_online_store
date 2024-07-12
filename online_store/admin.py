from django.contrib import admin
from .models import Feedback, Book, Category

admin.site.register(Feedback)
admin.site.register(Book)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name',)
    
    # Используйте raw_id_fields для выбора родительской категории 
    raw_id_fields = ('parent',)
    
admin.site.register(Category, CategoryAdmin)