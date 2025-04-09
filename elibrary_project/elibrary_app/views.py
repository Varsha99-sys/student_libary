from django.forms import ValidationError
from django.shortcuts import render,redirect
from .models import Book, IssuedItem
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from datetime import date
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponse

# Create your views here.
def home(req):
    return render(req,'home.html')


def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate user
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.info(request, "Invalid Credentials")
            return redirect("signin")

    return render(request, "signin.html")

def validate_password(password):
    # Check minimum length
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    # Check maximum length
    if len(password) > 128:
        raise ValidationError("Password cannot exceed 128 characters.")

    # Initialize flags for character checks
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    special_characters = "@$!%*?&"

    # Check for character variety
    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_characters:
            has_special = True

    if not has_upper:
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not has_lower:
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not has_digit:
        raise ValidationError("Password must contain at least one digit.")
    if not has_special:
        raise ValidationError(
            "Password must contain at least one special character (e.g., @$!%*?&)."
        )

    # Check against common passwords
    common_passwords = [
        "password",
        "123456",
        "qwerty",
        "abc123",
    ]  # Add more common passwords
    if password in common_passwords:
        raise ValidationError("This password is too common. Please choose another one.")



def register(req):
    context = {}
    if req.method == "POST":
        first_name = req.POST["first_name"]
        last_name = req.POST["last_name"]
        username = req.POST["username"]
        email = req.POST["email"]
        password1 = req.POST["password1"]
        password2 = req.POST["password2"]

        try:
            validate_password(password1)
        except ValidationError as e:
            context["errmsg"] = str(e)
            return render(req, "register.html", context) 

        if username == "" or password1 == "" or password2 == "":
            context["errmsg"] = "Field can't be empty"
            return render(req, "register.html", context)

        elif password1 != password2:
            context["errmsg"] = "Password and confirm password doesn't match"
            return render(req, "register.html", context)

        elif username.isdigit():
            context["errmsg"] = "Username can't be only number"
            return render(req, "register.html", context)
            
        elif password1 == username:
            context["errmsg"] = "Password cannot same as username"
            return render(req, "register.html", context)
        else:
            try:
                userdata = User.objects.create(username=username, password=password1)
                userdata.set_password(password1)
                userdata.save()
                print(User.objects.all())
                return redirect("signin")
            except:
                print("User already exists")
                context["errmsg"] = "User already exists"
                return render(req, "register.html", context)

        # if password1 == password2:
        #     if User.objects.filter(username=username).exists():
        #         messages.info(request, "Username already exists")
        #         return redirect("register")
        #     elif User.objects.filter(email=email).exists():
        #         messages.info(request, "Email already registered")
        #         return redirect("register")
        #     else:
        #         user = User.objects.create_user(
        #             first_name=first_name,
        #             last_name=last_name,
        #             username=username,
        #             email=email,
        #             password=password1,
        #         )
        #         user.save()
        #         return redirect("signin")
        # else:
        #     messages.info(request, "Passwords do not match")
        #     return redirect("register")
    
    return render(req, "register.html")

def request_password_reset(req):
    if req.method == "GET":
        return render(req, "request_password_reset.html")
    else:
        uname = req.POST.get("uname")
        context = {}
        try:
            userdata = User.objects.get(username=uname)
            return redirect("reset_password", uname=userdata.username)

        except User.DoesNotExist:
            context["errmsg"] = "No account found with this username"
            return render(req, "request_password_reset.html",context)

def reset_password(req, uname):
    userdata = User.objects.get(username=uname)
    if req.method == "GET":
        return render(req, "reset_password.html", {"user": userdata.username})
    else:
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        context = {}
        userdata = User.objects.get(username=uname)
        try:
            if upass == "" or ucpass == "":
                context["errmsg"] = "Field can't be empty"
                return render(req, "reset_password.html", context)
            elif upass != ucpass:
                context["errmsg"] = "Password and confirm password need to match"
                return render(req, "reset_password.html", context)
            else:
                # validate_password(upass)
                userdata.set_password(upass)
                userdata.save()
                return redirect("signin")

        except ValidationError as e:
            context["errmsg"] = str(e)
            return render(req, "reset_password.html", context)


def logout_view(req):
    logout(req)
    return redirect("home")

#issue-item view starts here
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Book, IssuedItem

@login_required(login_url=reverse_lazy("login"))
def issue_item(request):
    if request.method == "POST":
        # Get form data
        expected_return_date = request.POST.get("expected_return_date")  # Ensure this is not None
        return_date = request.POST.get("return_date")
        book_id = request.POST["book_id"]
        
        # Get the current book object
        current_book = Book.objects.get(id=book_id)
        
        # Check the user's current borrowed books count
        user_borrowed_books = IssuedItem.objects.filter(user_id=request.user, return_date__isnull=True).count()
        
        # Maximum books allowed to borrow
        max_books_allowed = 6
        
        # Check if user has already borrowed 6 books
        if user_borrowed_books >= max_books_allowed:
            messages.error(request, f"You can only borrow {max_books_allowed} books at a time.")
        elif current_book.quantity > 0:  # Only issue if the book is available
            # Create a new issued item record
            issue_item = IssuedItem.objects.create(
                user_id=request.user.id,
                book_id=current_book.id,
                expected_return_date=expected_return_date,
                return_date=return_date
            )
            issue_item.save()
            
            # Update the book quantity after issuing
            current_book.quantity -= 1
            current_book.save()

            messages.success(request, "Book issued successfully.")

            # Send email notification about the issue
            email = request.POST.get("email")
            if expected_return_date: 
                send_mail(
                    subject="Book issued successfully..",
                    message=f"Book issued successfully.. \n Kindly return your book before {expected_return_date} expected date.",
                    from_email=email,  # Change to your email
                    recipient_list=["sangalepearl99@gmail.com"],  # Your email
                    fail_silently=False,
                )
                
            # Check for overdue reminder (if the book's expected return date is today)
            expected_return_date = datetime.strptime(expected_return_date, "%Y-%m-%d") 
            if expected_return_date.date() == datetime.today().date(): 
                send_mail(
                    subject="Reminder Mail",
                    message=f"Hello student,\nPlease return your book.\nYou exceeded the expected return date {expected_return_date.date()}, and you may be required to pay for it.\nThank you.",
                    from_email="info@library.com",  # Change to your email
                    recipient_list=["sangalepearl99@gmail.com"],  # Your email
                    fail_silently=False,
                )
        else:
            messages.error(request, "This book is no longer available.")
    
    # Get books that are not yet issued to the user and have quantity > 0
    my_items = IssuedItem.objects.filter(user_id=request.user, return_date__isnull=True).values_list("book_id", flat=True)
    books = Book.objects.filter(quantity__gt=0).exclude(id__in=my_items)  # Only show books with quantity > 0

    return render(request, "issue_item.html", {'books': books})


# def issue_item(request):
#     books=Book.objects.all()
#     if request.method == "POST":
#         expected_return_date = request.POST.get("expected_return_date")  # Ensure this is not None
#         return_date = request.POST.get("return_date")
#         book_id = request.POST["book_id"]
#         current_book = Book.objects.get(id=book_id)
#         issue_item = IssuedItem.objects.create(user_id=request.user.id, book_id=current_book.id,expected_return_date=expected_return_date,return_date=return_date)
#         issue_item.save()
#         current_book.quantity -= 1
#         current_book.save()

#         messages.success(request, "Book issued successfully.")

#     # Get books that are not yet issued to the user
#     my_items = IssuedItem.objects.filter(user_id=request.user, return_date__isnull=True).values_list("book_id")
#     books = Book.objects.exclude(id__in=my_items).filter(quantity__gt=0)

#     return render(request, "issue_item.html",{'books':books})

from django.utils import timezone

# Return view to return book to library

@login_required(login_url=reverse_lazy("login"))
def return_item(request):
    if request.method == "POST":
        expected_return_date=request.POST.get('expected_return_date')
        # today = timezone.now().date()

        expected_return_date = IssuedItem.objects.filter(expected_return_date=expected_return_date)
        print(expected_return_date)
        if expected_return_date == datetime.today().date():            
            messages.warning(request, "Your return date has been passed! Please pay fine before returning the book.")
        return render(request,'payment.html')  # Give url name of your payment page here
    
    if request.method == "POST":
            book_id = request.POST["book_id"]
            current_book = Book.objects.get(id=book_id)  # This returns a single Book instance
            current_book.quantity += 1
            current_book.save()

            # Update the return date of the issued book
            issue_item = IssuedItem.objects.filter(user_id=request.user, book_id=current_book, return_date__isnull=True)
            issue_item.update(return_date=date.today())

            messages.success(request, "Book returned successfully.")

    # Get books that are issued to the user
    my_items = IssuedItem.objects.filter(user_id=request.user, return_date__isnull=True).values_list("book_id")
    books = Book.objects.filter(id__in=my_items)

    return render(request, "return_item.html", {"books": books})
    # else:
        
    # def return_item(request):
    #     book = IssuedItem.objects.get(expected_return_date)
        
    #     today = timezone.now().date()

    #     if book.expected_return_date < today:
    #         messages.warning(request, "Your return date has been passed! Please pay fine before returning the book.")
    #         return redirect('payment_page')  # Give url name of your payment page here
    
    #         return redirect('issued_book')

# @login_required(login_url=reverse_lazy("login"))
# def history(request):
   
#     return render(request, "history.html")

# History view to show the history of issued books to the user
@login_required(login_url=reverse_lazy("login"))
def history(request):
    my_items = IssuedItem.objects.filter(user_id=request.user).order_by("-issue_date")
    
    paginator = Paginator(my_items, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "history.html", {"books": page_obj})


from django.db.models import Q
from django.contrib import messages

def searchproduct(req):
    query=req.GET["q"]
    if query:
        books=Book.objects.filter(Q(book_name__icontains=query)
        |Q(author_name__icontains=query))

        if len(books)==0:
            messages.error(req,"No result found!!")
    else:
        books=Book.objects.all()
    
    context={'books':books}
    return render(req,'issue_item.html',context)

# search for study materials
from django.shortcuts import render
from django.db.models import Q
from django.contrib import messages
from .models import StudyMaterial

def searchproductstudy(req):
    query = req.GET.get("q") 
    books = StudyMaterial.objects.all() 
    print(books)
    if query:
        materials = StudyMaterial.objects.filter(
            Q(subject__icontains=query) | Q(author_name__icontains=query))
        print(materials,query)
        if not materials.exists():  
            messages.error(req, "No results found!") 
    else:
        messages.error(req, "No results found!") 
            
    context = {'materials': materials}

    return render(req, 'study_materials.html', context)

#Search books for readers
def searchproductreaders(req):
    query = req.GET.get("q") 
    books = ForReaders.objects.all() 
    print(books)
    if query:
        materials1 = ForReaders.objects.filter(
            Q(subject__icontains=query) | Q(author_name__icontains=query))
        print(materials1,query)
        if not materials1.exists():  
            messages.error(req, "No results found!") 
    else:
        messages.error(req, "No results found!") 
            
    context = {'materials1': materials1}

    return render(req, 'readers.html', context)

#Search for return book
def searchproductreturn(req):
    query=req.GET["q"]
    if query:
        books=Book.objects.filter(Q(book_name__icontains=query)
        |Q(author_name__icontains=query))

        if len(books)==0:
            messages.error(req,"No result found!!")
    else:
        books=Book.objects.all()
    
    context={'books':books}
    return render(req,'return_item.html',context)
#search for return books
# def searchproductreturn(req):
#     query=req.GET["q"]
#     if query:
#         # books1=IssuedItem.objects.filter(Q(issue_date__icontains=query))
#         books1 = Book.objects.filter(author_name__icontains=query)
#         if len(books1)==0:
#             messages.error(req,"No result found!!")
#         else:
#             books1=IssuedItem.objects.all()
    
#     context={'books1':books1}
#     return render(req,'return_item.html',context)

# def searchproductstudy(req):
#     query=req.GET["q"]
#     if query:
#         books=StudyMaterial.objects.filter(Q(subject__icontains=query)
#         |Q(author_name__icontains=query))

#         if len(books)==0:
#             messages.error(req,"No result found!!")
#         else:
#             books=StudyMaterial.objects.all()
    
#     context={'books':books}
#     return render(req,'study_materials.html',context)


from django.shortcuts import render, redirect
from .models import ReturnDate
from django.http import HttpResponse

def submit_return_date(request):
    if request.method == "POST":
        expected_return_date = request.POST.get("expected_return_date")  # Get input from form
        if expected_return_date:
            ReturnDate.objects.create(expected_return_date=expected_return_date)  # Save to DB
            return redirect('issue_item')  # Redirect to success page

    return render(request, 'issue_item.html')

from django.shortcuts import render, redirect
from django.core.mail import send_mail

import re
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        print(name,email,message)

        context={}
        if not re.match('^[a-zA-Z\s]*$', name):
                return render(request, "home.html", context)

        if name and email and message: 
            send_mail(
                subject="New Contact Form Submission",
                message=f"Name: {name}\nEmail: {email}\nMessage: {message}",
                from_email={email},  # Change to your email
                recipient_list=["sangalepearl99@gmail.com"],  # Your email
                fail_silently=False,
            )
            return redirect("/")  
    return render(request, "home.html") 


# def success_view(request):
#     return HttpResponse("<h2>Return date submitted successfully!</h2><a href='/submit/'>Submit another date</a>")


# def issue_book(request):
#     if request.method == "POST":
#         book_id = request.POST.get("book_id")  # Get book_id from form
#         book = Book.objects.get(id=book_id)  # Fetch the book from DB
#         book.quantity -= 1
#         book.save()
#         return HttpResponse(f"Book '{book.book_name}' has been issued!")  # Example response
       
#     return redirect("home")  # Redirect to home page if not a POST request



import smtplib
import sqlite3
from datetime import datetime, timedelta

# Email configuration
SMTP_SERVER = "smtp.gmail.com"  # Change this based on your email provider
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "your_password"  # Use an app password for security


def main():
    reminders = get_due_reminders()
    for email, _ in reminders:
        send_email(email)

if __name__ == "__main__":
    main()


from django.shortcuts import render
from .models import StudyMaterial,ForReaders

def study_material_list(request):
    materials = StudyMaterial.objects.all()
    return render(request, 'study_materials.html', {'materials': materials})



def readers(request):
    materials1 = ForReaders.objects.all()
    return render(request, 'readers.html',{'materials1': materials1})



from django.shortcuts import render, redirect
from django.contrib import messages

# import todo form and models

from .forms import TodoForm
from .models import Todo

def expected_book(request):

    item_list = Todo.objects.order_by("-date")
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('expected_book')
    form = TodoForm()

    page = {
        "forms": form,
        "list": item_list,
        "title": "TODO LIST",
    }
    return render(request, 'expected_book.html', page)


def remove(request, item_id):
    item = Todo.objects.get(id=item_id)
    item.delete()
    messages.info(request, "item removed !!!")
    return redirect('expected_book')


import random
from django.shortcuts import render
import razorpay

def payment(req):
    if request.method == "POST":
            book_id = request.POST["book_id"]
            current_book = Book.objects.get(id=book_id)  # This returns a single Book instance
            current_book.quantity += 1
            current_book.save()
            
            
            # Update the return date of the issued book
            issue_item = IssuedItem.objects.filter(user_id=request.user, book_id=current_book, return_date__isnull=True)
            issue_item.update(return_date=date.today())

            messages.success(request, "Book returned successfully.")

    # Get books that are issued to the user
    my_items = IssuedItem.objects.filter(user_id=request.user, return_date__isnull=True).values_list("book_id")
    books = Book.objects.filter(id__in=my_items)

    return render(request, "return_item.html", {"books": books})













   
    # if request.method == "POST":
     
    #     book_id = request.POST.get("book_id")  # Get book_id from form
    #     book = Book.objects.get(id=book_id)  # Fetch the book from DB
    #     book.quantity -= 1
    #     book.save()
     
    #     client = razorpay.Client(auth=("rzp_test_wH0ggQnd7iT3nB", "eZseshY3oSsz2fcHZkTiSlCm"))
    # # client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

    #     data = { "amount": 100, "currency": "INR", "receipt": "order_rcptid_11" }
    #     payment = client.order.create(data=data) 
    # # Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
    # return render(req, 'payment.html')

from django.shortcuts import render, get_object_or_404
import razorpay
from .models import ForReaders 
import razorpay
from django.shortcuts import render, redirect, get_object_or_404

def payment_reader(request, reader_id):
    reader = get_object_or_404(ForReaders, id=reader_id)

    if request.method == "POST":
        client = razorpay.Client(auth=("rzp_test_wH0ggQnd7iT3nB", "eZseshY3oSsz2fcHZkTiSlCm"))
        data = { "amount": 10000, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)

        # After Payment Success → Delete Reader or Book
        reader.delete()  # This will remove the reader entry (or book entry if book model)

        return redirect('readers')  # Redirect to readers page after payment

    return render(request, 'payment_reader.html', {'reader': reader})
