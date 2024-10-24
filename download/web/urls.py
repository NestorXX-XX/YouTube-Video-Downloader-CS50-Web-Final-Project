from django.urls import path
from . import views
urlpatterns = [
    path("",views.index, name="index"),
    path("login_view", views.login_view, name="login"),
    path("logout_view", views.logout_view, name="logout"),
    path("download", views.download , name="download"),
    path("history/new", views.history, name="history"),
    path("history/<str:user>", views.history, name="history"),
    path("history_view", views.history_view, name="history_view"),
    path("history_view_pages", views.history_view_pages, name="history_view_pages"),
    path("send_email", views.send_email_api, name="send_email"),
    path("contact_us", views.contact_us, name="contact_us"),
    path("contact_form", views.contact_form, name="contact_form"),
    
]