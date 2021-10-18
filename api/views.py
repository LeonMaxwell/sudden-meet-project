from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.views import APIView
from suddenuser.models import User
from .serializers import UserRegisterSerializers


class UserCreate(generics.CreateAPIView):
    """ Класс Generics с помощью которого происходит регистрация участника. """
    queryset = User
    serializer_class = UserRegisterSerializers
    permission_classes = (AllowAny, )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def grading(request, pk):
    pass
