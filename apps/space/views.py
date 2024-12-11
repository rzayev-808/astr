from django.shortcuts import render
from rest_framework.generics import GenericAPIView,RetrieveUpdateAPIView
from rest_framework.response import Response
from .serializers import SpaceSerializers,InviteSerializers,SpaceUpdateSerializers
from .models import Space
from rest_framework import status
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView



class GetSpaceVirews(mixins.ListModelMixin, mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericAPIView):

    serializer_class = SpaceSerializers
    
    def get_queryset(self):
        return Space.objects.filter(creater_user=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)




class SendInvite(APIView):
    def get_serializer(self, *args, **kwargs):
        return InviteSerializers(*args, **kwargs)
    
    def post(self, request, format=None):
        serializers = InviteSerializers(data=request.data)
        if serializers.is_valid():
            item = serializers.save()
            print(serializers.data["email"])
            return Response({"success":"Invite send to user"})
        

class SpaceDetailView(RetrieveUpdateAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceUpdateSerializers