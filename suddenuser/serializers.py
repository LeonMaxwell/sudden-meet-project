from rest_framework import serializers
from .models import User


class UserRegisterSerializers(serializers.ModelSerializer):
    """ Класс сериализатора для регистрации участника в системе. """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'longitude', 'latitude', 'gender', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

