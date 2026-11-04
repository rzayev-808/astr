"""Ümumi məktub göndərmə köməkçisi.

Hər məktubun iki şablonu olur — sadə mətn və HTML:
    <app>/templates/<app>/email/<ad>.txt
    <app>/templates/<app>/email/<ad>.html
HTML-i açmayan poçt proqramları mətn variantını göstərir.
"""
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_templated_email(*, subject, to, template, context):
    """Şablondan məktub düzəldib göndərir.

    template — uzantısız şablon yolu, məs. "invite/email/invite".
    Göndərmə alınmasa istisna (exception) atır; nə edəcəyinə çağıran tərəf qərar verir.
    """
    context = {"site_name": settings.SITE_NAME, **context}
    text_body = render_to_string(f"{template}.txt", context)
    html_body = render_to_string(f"{template}.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to] if isinstance(to, str) else list(to),
    )
    message.attach_alternative(html_body, "text/html")
    return message.send(fail_silently=False)
