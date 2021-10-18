from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from suddenuser.models import User, MatchSudden
from .serializers import UserRegisterSerializers
from rest_framework.response import Response
from django.db import IntegrityError


class UserCreate(generics.CreateAPIView):
    """ Класс Generics с помощью которого происходит регистрация участника. """
    queryset = User
    serializer_class = UserRegisterSerializers
    permission_classes = (AllowAny, )


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def grading(request, id):
    # Реализация обмена симпатиями между участниками
    mover = User.objects.get(pk=request.user.pk)
    matcher = User.objects.get(pk=id)
    if request.method == "GET":
        if request.user.pk == id:
            return Response("Вы самолюб! :)")
        else:
            try:
                suden = MatchSudden()
                suden.mover = mover
                suden.simpy = matcher
                respon = suden.mutual_sympathy()
                suden.save()
            except IntegrityError:
                respon = "Вы уже оценили этого участника"
            return Response(respon)


