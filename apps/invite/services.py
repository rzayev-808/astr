"""Dəvətin qəbul edilməsi — iş məntiqi bir yerdə.

Bu funksiyanı üç yer çağırır: id ilə qəbul, kodla qəbul və dəvətlə qeydiyyat.
"""


class InviteAcceptError(Exception):
    """Dəvət qəbul oluna bilmir; `status` HTTP kodu, mesaj isə istifadəçiyə göstərilir."""
    status = 400


class InviteEmailMismatch(InviteAcceptError):
    status = 403

    def __init__(self):
        super().__init__("This invite was not sent to your email")


class InviteAlreadyAccepted(InviteAcceptError):
    status = 400

    def __init__(self):
        super().__init__("Invite already accepted")


def accept_invite(invite, user):
    """Dəvəti `user` adına qəbul edir və onu space-in üzvü edir.

    Email uyğun gəlməsə InviteEmailMismatch, artıq qəbul olunubsa InviteAlreadyAccepted atır.
    """
    if invite.email.strip().lower() != user.email.strip().lower():
        raise InviteEmailMismatch()
    if invite.acceptance:
        raise InviteAlreadyAccepted()

    invite.acceptance = True
    invite.save(update_fields=["acceptance"])
    if invite.space:
        invite.space.members.add(user)
    return invite
