# accounts/views.py
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.throttling import UserRateThrottle
from django.contrib.auth.models import User

from .models import UserProfile
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializerV1,
    ProfileSerializerV2,
)
from rest_framework.authtoken.views import ObtainAuthToken


class RegisterView(APIView):
    """
    Register a new user. Returns the created user's id, username and token.
    (keeps behavior similar to earlier CreateAPIView but explicit here)
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token, _ = Token.objects.get_or_create(user=user)

        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "token": token.key,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Login view: returns token and basic user info.
    """
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        token_key = resp.data.get('token')
        if token_key:
            token = Token.objects.get(key=token_key)
            user = token.user
            return Response({'token': token.key, 'user_id': user.id, 'username': user.username})
        return resp


class ProfileV1View(APIView):
    """
    v1 endpoint for current user's profile (basic fields).
    URL: /api/v1/profile/
    Methods: GET, PUT
    """
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = [UserRateThrottle]

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializerV1(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializerV1(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfileV2View(APIView):
    """
    v2 endpoint for current user's profile (advanced fields).
    URL: /api/v2/profile/
    Methods: GET, PUT, DELETE
    """
    permission_classes = (permissions.IsAuthenticated,)
    throttle_classes = [UserRateThrottle]

    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializerV2(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        profile = request.user.profile
        # Accept multipart for avatar uploads; tests use multipart or json depending on setup
        serializer = ProfileSerializerV2(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        profile = request.user.profile
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
