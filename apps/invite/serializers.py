from rest_framework import serializers
from invite.models import *
from user.models import User


class InviteSerializers(serializers.ModelSerializer):

    class Meta:
        model = Invite
        exclude = ['acceptance', 'token']
        read_only_fields = ['invited_by']


class InviteListSerializers(serializers.ModelSerializer):

    class Meta:
        model = Invite
        exclude = ['token']


class InviteIncomingSerializer(serializers.ModelSerializer):
    """Mənə gələn dəvətlər (GET /invite/api/incoming/). Token göstərilmir; qəbul id ilə olur."""
    space_name = serializers.CharField(source='space.space_name', read_only=True, default=None)
    invited_by_name = serializers.CharField(source='invited_by.fullname', read_only=True, default=None)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Invite
        fields = ['id', 'email', 'role', 'space', 'space_name', 'invited_by_name',
                  'status', 'create_date']


class InvitePublicSerializer(InviteIncomingSerializer):
    """Linkdəki kodla açılan səhifə üçün — login tələb etmir.

    user_exists: dəvət olunan email ilə hesab var ya yox (front-end register/login seçir).
    is_current_user: sorğunu göndərən login olub və email-i dəvətdəki ilə eynidir.
    """
    user_exists = serializers.SerializerMethodField()
    is_current_user = serializers.SerializerMethodField()

    class Meta(InviteIncomingSerializer.Meta):
        fields = InviteIncomingSerializer.Meta.fields + ['user_exists', 'is_current_user']

    def get_user_exists(self, invite):
        return User.objects.filter(email__iexact=invite.email.strip()).exists()

    def get_is_current_user(self, invite):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return user.email.strip().lower() == invite.email.strip().lower()
