from django.urls import path
from rest_framework.throttling import ScopedRateThrottle
from . import views


app_name = 'users'

urlpatterns = [
    path('token/', views.TokenObtainPairView.as_view(throttle_classes=[ScopedRateThrottle]),
         name='token_obtain_pair'),
    path('token/refresh/', views.TokenRefreshView.as_view(throttle_classes=[ScopedRateThrottle]),
         name='token_refresh'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('email-verify/<token>/', views.VerifyEmailView.as_view(), name='email-verify'),
]
