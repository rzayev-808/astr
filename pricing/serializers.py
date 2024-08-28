from rest_framework import serializers
from .models import *

class PricingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Pricing
        fields = '__all__'