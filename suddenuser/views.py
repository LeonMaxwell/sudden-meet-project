from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from .models import User, MatchSudden
from .serializers import UserRegisterSerializers
from rest_framework.response import Response
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from django.db.models.expressions import RawSQL


def get_locations_nearby_coords(latitude, longitude, max_distance=None):
    """
    Return objects sorted by distance to specified coordinates
    which distance is less than max_distance given in kilometers
    """
    # Great circle distance formula
    gcd_formula = "6371 * acos(least(greatest(\
    cos(radians(%s)) * cos(radians(latitude)) \
    * cos(radians(longitude) - radians(%s)) + \
    sin(radians(%s)) * sin(radians(latitude)) \
    , -1), 1))"
    distance_raw_sql = RawSQL(
        gcd_formula,
        (latitude, longitude, latitude)
    )
    qs = User.objects.all().annotate(distance=distance_raw_sql).order_by('distance')
    if max_distance is not None:
        qs = qs.filter(distance__lt=max_distance)
    return qs


class EmployeeFilter(filters.FilterSet):
    """ Класс который подключает фильтрацию. """
    distance = filters.CharFilter(method='filter_queryset', label="Дистанция")

    class Meta:
        model = User
        fields = ['gender', 'first_name', 'last_name']

    def filter_queryset(self, queryset):
        queryset = User.objects.all()
        user_id = self.request.user.pk
        distance = self.request.query_params.get('distance')
        if user_id and distance:
            user = get_object_or_404(User, id=user_id)
            queryset = get_locations_nearby_coords(user.latitude, user.longitude, int(distance))
        return queryset


class UserListView(generics.ListAPIView):
    """ Класс для генерации списка из все участников. С фильтрацией по поле, имени и фамилии. """
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializers
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter


class UserCreate(generics.CreateAPIView):
    """ Класс Generics с помощью которого происходит регистрация участника. """
    queryset = User
    serializer_class = UserRegisterSerializers
    permission_classes = (AllowAny, )


@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def grading(request, pk):
    # Реализация обмена симпатиями между участниками
    mover = get_object_or_404(User, pk=request.user.pk)
    matcher = get_object_or_404(User, pk=pk)
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
            except IntegrityError as e:
                respon = "Вы уже оценили этого участника"
            return Response(respon)