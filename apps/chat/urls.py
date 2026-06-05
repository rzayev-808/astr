from django.urls import path
from .views import InboxView, DirectMessageView, SquadMessageView

urlpatterns = [
    path("api/direct/", InboxView.as_view(), name="chat_inbox"),
    path("api/direct/<int:user_id>/", DirectMessageView.as_view(), name="chat_direct"),
    path("api/squad/<int:squad_id>/", SquadMessageView.as_view(), name="chat_squad"),
]
