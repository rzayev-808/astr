from django.contrib import admin
from .models import DirectMessage, SquadMessage


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "is_read", "create_date")
    list_filter = ("is_read", "create_date")


@admin.register(SquadMessage)
class SquadMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "squad", "create_date")
    list_filter = ("squad", "create_date")
