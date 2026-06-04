from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("mainpage/", views.mainpage, name="mainpage"),

    path("api/qr-scan/", views.scan, name="qr_scan"),
    path("api/submit-details/", views.submit_details, name="submit_details"),
]