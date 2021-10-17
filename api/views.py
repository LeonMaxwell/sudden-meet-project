from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny

from suddenuser.models import User
from .serializers import UserRegisterSerializers


class UserCreate(generics.CreateAPIView):
    """ Класс Generics с помощью которого происходит регистрация участника. """
    queryset = User
    serializer_class = UserRegisterSerializers
    permission_classes = (AllowAny, )