from .models import User
from .serializers import *
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User #assuming you have a user model
from rest_framework import status
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import PasswordReset
from .emails import send_password_reset_email
from rest_framework import mixins
from rest_framework_simplejwt.views import TokenObtainPairView

class LoginView(TokenObtainPairView):
    """POST /auth/api/login/ — JWT verir; eyni anda bu email-ə gələn dəvətləri qəbul edir."""
    serializer_class = LoginSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer




class RequestPasswordReset(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=user.email, token=token)
            reset.save()

            # Link settings.PASSWORD_RESET_LINK-dən qurulur (bax: user/emails.py)
            if not send_password_reset_email(user, token):
                return Response(
                    {'error': 'Email could not be sent. Please try again later.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            return Response({'success': 'We have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with credentials not found"}, status=status.HTTP_404_NOT_FOUND)
        


class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = []

    def post(self, request, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        new_password = data['new_password']
        confirm_password = data['confirm_password']
        
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)
        
        reset_obj = PasswordReset.objects.filter(token=token).first()
        
        if not reset_obj:
            return Response({'error':'Invalid token'}, status=400)
        
        user = User.objects.filter(email=reset_obj.email).first()
        
        if user:
            user.set_password(request.data['new_password'])
            user.save()
            
            reset_obj.delete()
            
            return Response({'success':'Password updated'})
        else: 
            return Response({'error':'No user found'}, status=404)
        


class GetUserVirews(mixins.ListModelMixin, mixins.CreateModelMixin,mixins.UpdateModelMixin,mixins.RetrieveModelMixin,generics.GenericAPIView):

    serializer_class = UserGetAndDetailSerializers
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    

class DetailAndUpdateUser(generics.RetrieveUpdateAPIView):
    serializer_class = UserGetAndDetailSerializers
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

