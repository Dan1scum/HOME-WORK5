from django.urls import path
from .views import AuthorizationAPIView, RegistrationAPIView, ConfirmUserAPIView, GoogleOAuthAPIView, GoogleOAuthCallbackAPIView

urlpatterns = [
    path('auth/', AuthorizationAPIView.as_view(), name='auth'),
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('confirm/', ConfirmUserAPIView.as_view(), name='confirm'),
    path('oauth/google/', GoogleOAuthAPIView.as_view(), name='google_oauth'),
    path('oauth/google/callback/', GoogleOAuthCallbackAPIView.as_view(), name='google_oauth_callback'),
]