from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_direct(message_data, user_a_id, user_b_id):
    """Direct mesajı hər iki tərəfin canlı söhbət qrupuna yayımla (məs. fayl mesajı)."""
    layer = get_channel_layer()
    if layer is None:
        return
    a, b = sorted([user_a_id, user_b_id])
    async_to_sync(layer.group_send)(
        f"dm_{a}_{b}", {"type": "chat.message", "message": message_data}
    )


def broadcast_squad(message_data, squad_id):
    """Squad mesajını squad-ın canlı söhbət qrupuna yayımla (məs. fayl mesajı)."""
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        f"squad_{squad_id}", {"type": "chat.message", "message": message_data}
    )
