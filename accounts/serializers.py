# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email','first_name','last_name')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    class Meta:
        model = User
        fields = ('username','email','password','first_name','last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            username = validated_data['username'],
            email = validated_data.get('email',''),
            password = validated_data['password'],
            first_name = validated_data.get('first_name',''),
            last_name = validated_data.get('last_name','')
        )
        return user

class ProfileSerializerV1(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    phone = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = UserProfile
        fields = ('user','phone','created_at','updated_at')

class ProfileSerializerV2(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    phone = serializers.CharField(allow_blank=True, required=False)
    bio = serializers.CharField(allow_blank=True, required=False)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = UserProfile
        fields = ('user','phone','bio','avatar','created_at','updated_at')
