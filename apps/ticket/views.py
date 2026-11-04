from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from django_filters import rest_framework as filters
from simple_history.models import HistoricalRecords


class TicketViewset(viewsets.ModelViewSet):  
    serializer_class = TicketViewSerializers
    
    def get_queryset(self):
        return Ticket.objects.filter(user_id=self.request.user.id)
    
    
class TicketCreateViewset(viewsets.ModelViewSet):  
    serializer_class = TicketCreateEditSerializers
    
    def get_queryset(self):
        # Redaktə/silmə yalnız öz ticket-ləri üçün
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return Ticket.objects.none()
        return Ticket.objects.filter(user=self.request.user)


class AnsweCreateViewset(viewsets.ModelViewSet):
    serializer_class = AnswerSerializers
    def get_queryset(self):
        return Answer.objects.all()
    
