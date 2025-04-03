from django import forms
from .models import Book

class IssueBookForm(forms.Form):
    book_id = forms.IntegerField(widget=forms.HiddenInput())


from django import forms
from .models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = "__all__"
