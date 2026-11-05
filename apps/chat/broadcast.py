import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def _send_to_group(group_name, message_data):
    """Mesajı canlı söhbət qrupuna yayımla.

    Mesaj artıq bazaya yazılıb. Canlı yayım alınmasa (məs. Redis işləmir və ya
    ona qoşulmaq olmur) sorğu xəta ilə bitməməlidir: səbəb log-a yazılır,
    mesaj isə siyahıda (GET) görünür.
    """
    try:
        layer = get_channel_layer()
        if layer is None:
            return False
        async_to_sync(layer.group_send)(
            group_name, {"type": "chat.message", "message": message_data}
        )
        return True
    except Exception:
        logger.exception("Canlı chat yayımı alınmadı (Redis işləyirmi?): qrup=%s", group_name)
        return False


def broadcast_direct(message_data, user_a_id, user_b_id):
    """Direct mesajı hər iki tərəfin canlı söhbət qrupuna yayımla (məs. fayl mesajı)."""
    a, b = sorted([user_a_id, user_b_id])
    return _send_to_group(f"dm_{a}_{b}", message_data)


def broadcast_squad(message_data, squad_id):
    """Squad mesajını squad-ın canlı söhbət qrupuna yayımla (məs. fayl mesajı)."""
    return _send_to_group(f"squad_{squad_id}", message_data)
