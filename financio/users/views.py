import jwt
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.sites.shortcuts import get_current_site
from django.middleware import csrf
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)
from rest_framework import generics, status

from users.models import CustomUser
from users.serializers import RegisterSerializer
from users.utils import Util


class TokenObtainPairView(BaseTokenObtainPairView):
    throttle_scope = 'token_obtain'

    def post(self, request: Request, *args, **kwargs) -> Response:
        data = request.data
        response = Response()
        email = data.get('email', None)
        password = data.get('password', None)
        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                data = Util.get_tokens_for_user(user)
                response.set_cookie(
                    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                    value=data["access"],
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
                )
                csrf.get_token(request)
                response.data = {"Success": "Login successfully", "data": data}
                return response
            else:
                return Response({"No active": "This account is not active!!"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"Invalid": "Invalid username or password!!"}, status=status.HTTP_404_NOT_FOUND)


class TokenRefreshView(BaseTokenRefreshView):
    throttle_scope = 'token_refresh'


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny, )

    def perform_create(self, serializer):
        user = serializer.save()
        token = RefreshToken.for_user(user).access_token
        message_data = {
            'subject': 'Verify your email',
            'body': ' Use the link below to verify your email \n'
        }
        Util.send_email(get_current_site(self.request).domain, 'users:email-verify', user, token, message_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VerifyEmailView(APIView):
    """
    A view for verifying user email activation tokens.

    This view handles GET requests with an activation token in the URL.
    If the token is valid and not expired, it activates the user associated with the token.

    Attributes:
    - permission_classes: The list of permission classes applied to this view.
    """
    permission_classes = [AllowAny]

    def get(self, request, token):
        """
        Handle GET requests to verify email activation.

        Parameters:
        - request: The request object.
        - token: The activation token extracted from the URL.

        Returns:
        - A Response object with the result of the email verification.
            - If the token is valid and the associated user is successfully activated,
            returns a success message with HTTP status code 200.
            - If the token is expired, returns an error message indicating the activation has expired
            with HTTP status code 400.
            - If the token is invalid, returns an error message indicating an invalid token
            with HTTP status code 400.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, settings.SIMPLE_JWT['ALGORITHM'])
            user = CustomUser.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
