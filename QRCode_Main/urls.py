from django.urls import path
from . import views

urlpatterns = [
    path("api/submit-details/", views.submit_details),
]