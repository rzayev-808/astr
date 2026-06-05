from rest_framework import serializers
from .models import DirectMessage, SquadMessage
from user.serializers import UserGetAndDetailSerializers


class DirectMessageSerializer(serializers.ModelSerializer):
    sender_detail = UserGetAndDetailSerializers(source="sender", read_only=True)
    receiver_detail = UserGetAndDetailSerializers(source="receiver", read_only=True)

    class Meta:
        model = DirectMessage
        fields = [
            "id", "sender", "receiver", "sender_detail", "receiver_detail",
            "text", "file", "is_read", "create_date",
        ]
        read_only_fields = ["sender", "receiver", "is_read", "create_date"]

    def validate(self, attrs):
        if not attrs.get("text") and not attrs.get("file"):
            raise serializers.ValidationError(
                "Mesaj boş ola bilməz: ya mətn, ya da fayl göndərin."
            )
        return attrs


class SquadMessageSerializer(serializers.ModelSerializer):
    sender_detail = UserGetAndDetailSerializers(source="sender", read_only=True)

    class Meta:
        model = SquadMessage
        fields = ["id", "sender", "squad", "sender_detail", "text", "file", "create_date"]
        read_only_fields = ["sender", "squad", "create_date"]

    def validate(self, attrs):
        if not attrs.get("text") and not attrs.get("file"):
            raise serializers.ValidationError(
                "Mesaj boş ola bilməz: ya mətn, ya da fayl göndərin."
            )
        return attrs
