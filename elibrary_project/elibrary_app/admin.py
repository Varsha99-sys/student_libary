from django.contrib import admin
from .models import Book, IssuedItem

# Register your models here.

# Custom admin class for Book model
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'author_name', 'quantity', 'subject', 'book_add_date', 'book_add_time')
    list_filter = ('author_name', 'subject')
    search_fields = ('book_name', 'author_name', 'subject')
    ordering = ('book_name',)


# Custom admin class for IssuedItem model
class IssuedItemAdmin(admin.ModelAdmin):
    list_display = ('book_name', 'username', 'issue_date','expected_return_date','return_date')
    list_filter = ('issue_date', 'expected_return_date','return_date')
    search_fields = ('book_name', 'username')
    ordering = ('-issue_date',)
    
    # To show the book name and username from the related models
    def book_name(self, obj):
        return obj.book.book_name

    def username(self, obj):
        return obj.user.username

    book_name.admin_order_field='book'
    book_name.short_description='Book'

# Registering the models and the custom admin classes
admin.site.register(Book, BookAdmin)
admin.site.register(IssuedItem, IssuedItemAdmin)

from django.contrib import admin
from .models import StudyMaterial

# pdf admin
@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title','subject', 'author_name','images')


