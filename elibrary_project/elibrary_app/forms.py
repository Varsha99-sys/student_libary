from django import forms
from .models import Book

class IssueBookForm(forms.Form):
    book_id = forms.IntegerField(widget=forms.HiddenInput())


