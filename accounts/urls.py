# accounts/urls.py
from django.urls import path
from .views import (
    RegisterView,
    CustomObtainAuthToken,
    ProfileV1View,
    ProfileV2View,
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', CustomObtainAuthToken.as_view(), name='login'),

    # Versioned profile endpoints (current-user focused)
    path('v1/profile/', ProfileV1View.as_view(), name='profile-v1'),
    path('v2/profile/', ProfileV2View.as_view(), name='profile-v2'),
]
