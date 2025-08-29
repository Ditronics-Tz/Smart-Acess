from rest_framework import serializers
from .models import SecurityPersonnel, PhysicalLocations, AccessGates
from datetime import date

class SecurityPersonnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityPersonnel
        exclude = ['hire_date']

    def create(self, validated_data):
        validated_data['hire_date'] = date.today()
        return super().create(validated_data)

class PhysicalLocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalLocations
        fields = '__all__'

class AccessGatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessGates
        fields = '__all__'
