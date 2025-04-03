
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone


# ----------- Library Management System Models ------------

# Book model to store book details
class Book(models.Model):
    book_name = models.CharField(max_length=150)
    author_name = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    subject = models.CharField(max_length=2000)
    book_add_time = models.DateTimeField(default=timezone.now)  # Changed to DateTimeField for both date and time
    book_add_date = models.DateField(default=date.today)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["book_name", "author_name"], name="unique_book_author")  # Replaced unique_together with UniqueConstraint
        ]

    def __str__(self):
        return self.book_name


# IssuedItem model to store issued book details

class IssuedItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    issue_date = models.DateField(default=date.today)
    expected_return_date=models.DateField()
    return_date = models.DateField(blank=True, null=True)

    # property to get book name
    @property
    def book_name(self):
        return self.book.book_name

    # property to get author name
    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return f"{self.book.book_name} issued by {self.user.first_name} on {self.issue_date}"


from django.db import models

class ReturnDate(models.Model):
    expected_return_date = models.DateField()

    def __str__(self):
        return str(self.return_date)


from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# pdf model
from django.db import models

class StudyMaterial(models.Model):
    title = models.CharField(max_length=255)
    subject=models.CharField(max_length=200)
    author_name=models.CharField(max_length=200)
    images = models.ImageField(upload_to="photos")
    pdf = models.FileField(upload_to='study_materials/')  # Uploads to MEDIA_ROOT/study_materials

    def __str__(self):
        return self.title

class ForReaders(models.Model):
    title = models.CharField(max_length=255)
    subject=models.CharField(max_length=200)
    author_name=models.CharField(max_length=200)
    amount=models.PositiveIntegerField()
    images = models.ImageField(upload_to="photos")
    def __str__(self):
        return self.title


from django.utils import timezone


class Todo(models.Model):
    title = models.CharField(max_length=100)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
       

