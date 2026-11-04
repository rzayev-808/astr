"""Dəvət məktubu."""
import logging

from django.conf import settings

from app.mailer import send_templated_email

logger = logging.getLogger(__name__)


def build_invite_link(invite):
    return settings.INVITE_LINK.format(id=invite.pk)


def send_invite_email(invite):
    """Dəvət olunan ünvana məktub göndərir.

    Uğurlu olsa True, alınmasa False qaytarır (xəta log-a yazılır).
    Məktub getməsə də dəvət bazada qalır — sorğu çökmür.
    """
    inviter = invite.invited_by.fullname if invite.invited_by else "Someone"
    space_name = invite.space.space_name if invite.space else None
    if space_name:
        subject = f"{inviter} invited you to {space_name}"
    else:
        subject = f"{inviter} invited you to {settings.SITE_NAME}"

    context = {
        "inviter": inviter,
        "space_name": space_name,
        "role": invite.role,
        "email": invite.email,
        "link": build_invite_link(invite),
    }
    try:
        send_templated_email(
            subject=subject,
            to=invite.email,
            template="invite/email/invite",
            context=context,
        )
        return True
    except Exception:
        logger.exception("Dəvət məktubu göndərilmədi: invite_id=%s to=%s", invite.pk, invite.email)
        return False
