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
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    location_type = serializers.CharField(source='location.location_type', read_only=True)

    class Meta:
        model = AccessGates
        fields = '__all__'

class DatabaseBackupSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    backup_file = serializers.CharField(read_only=True)

class DatabaseRestoreSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)

class DatabaseBackupListSerializer(serializers.Serializer):
    backups = serializers.ListField(child=serializers.CharField(), read_only=True)
