from django.urls import path
from .views import UserCreate


urlpatterns = [
    path('clients/create/', UserCreate.as_view(), name="register"),
]