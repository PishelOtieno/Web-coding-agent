"""Accounts app URLs."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, CustomTokenObtainPairView, UserViewSet

register_view = RegisterView.as_view({'post': 'register'})
user_list = UserViewSet.as_view({'get': 'me'})
user_profile = UserViewSet.as_view({'put': 'update_profile', 'patch': 'update_profile'})

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', user_list, name='user_profile'),
    path('profile/update/', user_profile, name='update_profile'),
]
