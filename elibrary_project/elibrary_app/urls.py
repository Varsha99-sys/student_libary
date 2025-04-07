from django.urls import path
from . import views
from .views import contact_view


urlpatterns = [

    path("", views.home, name="home"),  # Home page
    path("issue_item/", views.issue_item, name="issue_item"),  # Book issue page
    path("signin/", views.login_user, name="signin"),  # Login page
    path("register", views.register, name="register"),  # Registration page
    path("logout", views.logout_view, name="logout"),  # Logout page
    path("return_item", views.return_item, name="return_item"),  # Return item page
    
    path("history", views.history, name="history"),  # History page for issued book
    path(
        "request_password_reset/",
        views.request_password_reset,
        name="request_password_reset",
    ),
    path("reset_password/<uname>/", views.reset_password, name="reset_password"),
    path('searchproduct/',views.searchproduct,name='searchproduct'),
    path('searchproductstudy/',views.searchproductstudy,name='searchproductstudy'),
    path('searchproductreturn/',views.searchproductreturn,name='searchproductreturn'),
    path('submit/', views.submit_return_date, name='submit_return_date'),
    path("contact_view/", views.contact_view, name="contact_view"),
    path('study-materials/', views.study_material_list, name='study_material_list'),
    path('readers/', views.readers, name='readers'),
    path('searchproductreaders/', views.searchproductreaders, name='searchproductreaders'),
    path('payment/<int:reader_id>/',views.payment,name='payment'),
    path('expected_book/',views.expected_book,name='expected_book'),
    path('del/<str:item_id>', views.remove, name="del"),
    # path('admin/', admin.site.urls),
] 
