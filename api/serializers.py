from rest_framework import serializers
from suddenuser.models import User


class UserRegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'gender', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True }}
