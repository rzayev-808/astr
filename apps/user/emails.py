"""Şifrə sıfırlama məktubu."""
import logging

from django.conf import settings

from app.mailer import send_templated_email

logger = logging.getLogger(__name__)


def build_password_reset_link(token):
    return settings.PASSWORD_RESET_LINK.format(token=token)


def send_password_reset_email(user, token):
    """İstifadəçiyə şifrə sıfırlama linki göndərir.

    Uğurlu olsa True, alınmasa False qaytarır (xəta log-a yazılır).
    """
    context = {
        "fullname": user.fullname,
        "email": user.email,
        "link": build_password_reset_link(token),
    }
    try:
        send_templated_email(
            subject=f"Reset your {settings.SITE_NAME} password",
            to=user.email,
            template="user/email/password_reset",
            context=context,
        )
        return True
    except Exception:
        logger.exception("Şifrə sıfırlama məktubu göndərilmədi: user_id=%s to=%s", user.pk, user.email)
        return False
