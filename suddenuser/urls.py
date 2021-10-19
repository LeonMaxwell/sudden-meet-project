from django.urls import path, include
from .views import UserCreate, grading, UserListView


urlpatterns = [
    path('clients/create/', UserCreate.as_view(), name="register"),
    path('clients/auth/', include('rest_framework.urls'), name="auth"),
    path('clients/<int:pk>/match/', grading, name="grading"),
    path('list/', UserListView.as_view(), name="listuser")
]