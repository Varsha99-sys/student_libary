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
@login_required(login_url=reverse_lazy("login"))
def issue_item(request):
    if request.method == "POST":
        expected_return_date = request.POST.get("expected_return_date")  # Ensure this is not None
        return_date = request.POST.get("return_date")
        book_id = request.POST["book_id"]
        current_book = Book.objects.get(id=book_id)
        
        if current_book.quantity > 0:  # Only issue if the book is available
            issue_item = IssuedItem.objects.create(
                user_id=request.user.id,
                book_id=current_book.id,
                expected_return_date=expected_return_date,
                return_date=return_date
            )
            issue_item.save()
            current_book.quantity -= 1
            current_book.save()

            messages.success(request, "Book issued successfully.")
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


# Return view to return book to library
@login_required(login_url=reverse_lazy("login"))
def return_item(request):
    if request.method == "POST":
        book_id = request.POST["book_id"]
        # current_book = Book.objects.all()
        # print(current_book)
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
    query = req.GET.get("q", "")  # Get the query parameter from GET request
    books = StudyMaterial.objects.all()  # Default: show all books if no query
    print(books)
    if query:
        materials = StudyMaterial.objects.filter(
            Q(subject__icontains=query) | Q(author_name__icontains=query))
        print(materials,query)
        if not materials.exists():  # If no books match the search, show a message
            messages.error(req, "No results found!") 
    context = {'materials': materials, 'query': query}
    return render(req, 'study_materials.html', context)

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
from django.http import HttpResponse

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

            # raise ValidationError('Name should only contain alphabetic characters and spaces.')

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

def get_due_reminders():
    """Fetch records where expected_return_date is in 2 days."""
    conn = sqlite3.connect("database.db")  # Replace with your database
    cursor = conn.cursor()
    due_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
  
    cursor.execute("SELECT email, expected_return_date FROM users WHERE expected_return_date = ?", (due_date,))
    reminders = cursor.fetchall()
    
    conn.close()
    return reminders

def send_email(to_email):
    """Send reminder email with an HTML file link."""
    subject = "Reminder: Upcoming Return Due Date"
    html_url = "/https://example.com/reminder.html"  # Replace with actual HTML file URL
    body = f"""
    Hello,<br><br><br>
    T/his is a reminder that your item is due for return in 2 days. Please ensure timely return.<br>
    <a href='{html_url}'>Click here</a> for more details.<br><br>
    ank you!
    """
    
    message = f"Subject: {subject}\nContent-Type: text/html\n\n{body}"
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, message)
        server.quit()
        print(f"Reminder sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def main():
    reminders = get_due_reminders()
    for email, _ in reminders:
        send_email(email)

if __name__ == "__main__":
    main()


from django.shortcuts import render
from .models import StudyMaterial

def study_material_list(request):
    materials = StudyMaterial.objects.all()
    return render(request, 'study_materials.html', {'materials': materials})
