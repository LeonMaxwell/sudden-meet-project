from django.urls import path, include
from .views import UserCreate


urlpatterns = [
    path('clients/create/', UserCreate.as_view(), name="register"),
    path('clients/auth/', include('rest_framework.urls'))
]