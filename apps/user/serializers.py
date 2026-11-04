from rest_framework import serializers
from .models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from invite.models import Invite
from invite.services import accept_invite, accept_pending_invites_for
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )
    fullname = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    # Dəvət linkindən gələn qeydiyyat: məktubdakı gizli kod. Varsa, hesab yaranan kimi
    # dəvət qəbul olunur və adam space-ə düşür. Cavabda həmin space-in id-si qayıdır.
    invite_token = serializers.CharField(write_only=True, required=False, allow_blank=True)
    space = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'fullname', 'invite_token', 'space')
        extra_kwargs = {
            'fullname': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        token = attrs.pop('invite_token', '') or ''
        self._invite = None
        if token:
            invite = Invite.objects.filter(token=token).first()
            if invite is None:
                raise serializers.ValidationError({"invite_token": "Invalid invite"})
            if invite.acceptance:
                raise serializers.ValidationError({"invite_token": "Invite already accepted"})
            if invite.email.strip().lower() != attrs['email'].strip().lower():
                raise serializers.ValidationError(
                    {"invite_token": "This invite was sent to a different email"})
            self._invite = invite

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            fullname=validated_data['fullname'],
            email=validated_data['email'],
        )
        
        user.set_password(validated_data['password'])
        user.save()

        # Linkdəki kodla gələn dəvət + bu email-ə gələn digər gözləyən dəvətlər avtomatik qəbul olunur
        if self._invite is not None:
            accept_invite(self._invite, user)
        self._accepted = accept_pending_invites_for(user)

        return user

    def get_space(self, user):
        """Qeydiyyatla birlikdə qəbul olunan dəvətin space id-si (front-end adamı ora apara bilər)."""
        invite = getattr(self, '_invite', None)
        if invite is not None:
            return invite.space_id
        accepted = getattr(self, '_accepted', None) or []
        return accepted[0].space_id if accepted else None
        

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.RegexField(
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        write_only=True,
        error_messages={'invalid': ('Password must be at least 8 characters long with at least one capital letter and symbol')})
    confirm_password = serializers.CharField(write_only=True, required=True)


class UserGetAndDetailSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password','is_admin','last_login','is_active']

class LoginSerializer(TokenObtainPairSerializer):
    """Adi JWT login + login olan kimi bu email-ə gələn gözləyən dəvətlər qəbul olunur."""

    def validate(self, attrs):
        data = super().validate(attrs)
        accept_pending_invites_for(self.user)
        return data
