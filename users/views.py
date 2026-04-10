from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .serializers import UserCreateSerializer, UserAuthSerializer, ConfirmUserSerializer
from django.contrib.auth import authenticate
from .models import ConfirmationCode
from rest_framework.views import APIView
import random
from django.contrib.auth import get_user_model
import requests
import os
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
import redis
from django.conf import settings

User = get_user_model()


class AuthorizationAPIView(APIView):
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        return Response({'error': 'user credentials are wrong!'}, status=status.HTTP_401_UNAUTHORIZED)


class RegistrationAPIView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = User.objects.create_user(email=email, password=password, is_active=False)

        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        # Save code in Redis with TTL 5 minutes
        r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        r.setex(f'confirmation_code:{email}', 300, code)

        print(f'Код подтверждения для пользователя {email}: {code}')  # Для отладки

        return Response(
            {'user_id': user.id, 'detail': 'Пользователь создан. Проверьте код подтверждения.'},
            status=status.HTTP_201_CREATED
        )


class ConfirmUserAPIView(APIView):
    def post(self, request):
        serializer = ConfirmUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Пользователь подтвержден и активирован"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleOAuthAPIView(APIView):
    def get(self, request):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        redirect_uri = 'http://127.0.0.1:8000/api/v1/users/oauth/google/callback/'
        scope = 'openid email profile'
        auth_url = f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}'
        return redirect(auth_url)


class GoogleOAuthCallbackAPIView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return Response({'error': 'No code provided'}, status=status.HTTP_400_BAD_REQUEST)

        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        redirect_uri = 'http://127.0.0.1:8000/api/v1/users/oauth/google/callback/'

        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_url, data=data)
        if response.status_code != 200:
            return Response({'error': 'Failed to get token'}, status=status.HTTP_400_BAD_REQUEST)

        token_data = response.json()
        access_token = token_data.get('access_token')

        # Get user info
        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        if user_response.status_code != 200:
            return Response({'error': 'Failed to get user info'}, status=status.HTTP_400_BAD_REQUEST)

        user_info = user_response.json()
        email = user_info.get('email')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')

        # Create or update user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'registration_source': 'google',
                'is_active': True
            }
        )
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.registration_source = 'google'
            user.is_active = True
        user.last_login = timezone.now()
        user.save()

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)

        # Redirect to frontend or return token
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
