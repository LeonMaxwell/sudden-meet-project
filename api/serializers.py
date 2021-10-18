from rest_framework import serializers
from suddenuser.models import User


class UserRegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'gender', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

