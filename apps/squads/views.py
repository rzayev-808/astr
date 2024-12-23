from django.shortcuts import render
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView
from rest_framework.response import Response
from .models import Squad
from .serializers import SquadSerializers
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

class SquadetailView(viewsets.ViewSet):
   def retrieve(self, request, pk=None):
        queryset = Squad.objects.all()
        data = get_object_or_404(queryset, pk=pk)
        serializer = SquadSerializers(data)
        return Response(serializer.data)