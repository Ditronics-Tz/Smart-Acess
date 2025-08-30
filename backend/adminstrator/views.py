from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import SecurityPersonnel , PhysicalLocations, AccessGates
from .serializers import SecurityPersonnelSerializer, PhysicalLocationsSerializer, AccessGatesSerializer
from .permissions import IsAdministrator
import os
from datetime import datetime
import subprocess

class SecurityPersonnelPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class SecurityPersonnelCreateView(generics.CreateAPIView):
	queryset = SecurityPersonnel.objects.all()
	serializer_class = SecurityPersonnelSerializer
	permission_classes = [IsAdministrator]

class SecurityPersonnelListView(generics.ListAPIView): #list of secuirty perosnnel w filter
    queryset = SecurityPersonnel.objects.filter(deleted_at__isnull=True)  # Exclude soft-deleted
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAdministrator]
    pagination_class = SecurityPersonnelPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['full_name', 'employee_id', 'badge_number']
    ordering_fields = ['full_name', 'employee_id', 'badge_number', 'hire_date', 'created_at']
    ordering = ['-created_at']

class SecurityPersonnelDetailView(generics.RetrieveAPIView): #for single secuirty-personnel info
    queryset = SecurityPersonnel.objects.all()
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'security_id'

class SecurityPersonnelUpdateView(generics.UpdateAPIView): # for both full (PUT) and partial (PATCH) update of security personnel
    queryset = SecurityPersonnel.objects.all()
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'security_id'

class SecurityPersonnelDeleteView(generics.DestroyAPIView): # for soft delete of security personnel
    queryset = SecurityPersonnel.objects.all()
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'security_id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Perform soft delete
        instance.deleted_at = timezone.now()
        instance.is_active = False
        instance.save(update_fields=['deleted_at', 'is_active'])
        
        return Response({
            'message': 'Security personnel soft deleted successfully',
            'deleted_at': instance.deleted_at,
            'is_active': instance.is_active
        }, status=status.HTTP_200_OK)  ##ive have to fix 404 error

class SecurityPersonnelRestoreView(APIView): # for restoring soft-deleted security personnel
    permission_classes = [IsAdministrator]
    
    def post(self, request, security_id):
        # Get the security personnel record (including soft-deleted ones)
        try:
            instance = SecurityPersonnel.objects.get(security_id=security_id)
        except SecurityPersonnel.DoesNotExist:
            return Response({
                'error': 'Security personnel not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the record is actually soft-deleted
        if instance.deleted_at is None:
            return Response({
                'error': 'Security personnel is not deleted and cannot be restored'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Restore the record
        instance.deleted_at = None
        instance.is_active = True
        instance.save(update_fields=['deleted_at', 'is_active'])
        
        # Return the restored record
        serializer = SecurityPersonnelSerializer(instance)
        return Response({
            'message': 'Security personnel restored successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)


# PhysicalLocations Views
class PhysicalLocationsCreateView(generics.CreateAPIView):
    queryset = PhysicalLocations.objects.all()
    serializer_class = PhysicalLocationsSerializer
    permission_classes = [IsAdministrator]

class PhysicalLocationsListView(generics.ListAPIView):
    queryset = PhysicalLocations.objects.filter(deleted_at__isnull=True)  # Exclude soft-deleted
    serializer_class = PhysicalLocationsSerializer
    permission_classes = [IsAdministrator]
    pagination_class = SecurityPersonnelPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['location_type', 'is_restricted']
    search_fields = ['location_name']
    ordering_fields = ['location_name', 'location_type', 'created_at']
    ordering = ['-created_at']

class PhysicalLocationsDetailView(generics.RetrieveAPIView):
    queryset = PhysicalLocations.objects.all()
    serializer_class = PhysicalLocationsSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'location_id'

class PhysicalLocationsUpdateView(generics.UpdateAPIView):
    queryset = PhysicalLocations.objects.all()
    serializer_class = PhysicalLocationsSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'location_id'

class PhysicalLocationsDeleteView(generics.DestroyAPIView):
    queryset = PhysicalLocations.objects.all()
    serializer_class = PhysicalLocationsSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'location_id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Perform soft delete
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        
        return Response({
            'message': 'Physical location soft deleted successfully',
            'deleted_at': instance.deleted_at
        }, status=status.HTTP_200_OK)

class PhysicalLocationsRestoreView(APIView):
    permission_classes = [IsAdministrator]
    
    def post(self, request, location_id):
        try:
            instance = PhysicalLocations.objects.get(location_id=location_id)
        except PhysicalLocations.DoesNotExist:
            return Response({
                'error': 'Physical location not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if instance.deleted_at is None:
            return Response({
                'error': 'Physical location is not deleted and cannot be restored'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.deleted_at = None
        instance.save(update_fields=['deleted_at'])
        
        serializer = PhysicalLocationsSerializer(instance)
        return Response({
            'message': 'Physical location restored successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

# AccessGates Views
class AccessGatesCreateView(generics.CreateAPIView):
    queryset = AccessGates.objects.all()
    serializer_class = AccessGatesSerializer
    permission_classes = [IsAdministrator]

class AccessGatesListView(generics.ListAPIView):
    queryset = AccessGates.objects.filter(deleted_at__isnull=True)  # Exclude soft-deleted
    serializer_class = AccessGatesSerializer
    permission_classes = [IsAdministrator]
    pagination_class = SecurityPersonnelPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['gate_type', 'status', 'location']
    search_fields = ['gate_code', 'gate_name', 'hardware_id']
    ordering_fields = ['gate_name', 'gate_code', 'created_at']
    ordering = ['-created_at']

class AccessGatesDetailView(generics.RetrieveAPIView):
    queryset = AccessGates.objects.all()
    serializer_class = AccessGatesSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'gate_id'

class AccessGatesUpdateView(generics.UpdateAPIView):
    queryset = AccessGates.objects.all()
    serializer_class = AccessGatesSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'gate_id'

class AccessGatesDeleteView(generics.DestroyAPIView):
    queryset = AccessGates.objects.all()
    serializer_class = AccessGatesSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'gate_id'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Perform soft delete
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        
        return Response({
            'message': 'Access gate soft deleted successfully',
            'deleted_at': instance.deleted_at
        }, status=status.HTTP_200_OK)

class AccessGatesRestoreView(APIView):
    permission_classes = [IsAdministrator]
    
    def post(self, request, gate_id):
        try:
            instance = AccessGates.objects.get(gate_id=gate_id)
        except AccessGates.DoesNotExist:
            return Response({
                'error': 'Access gate not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if instance.deleted_at is None:
            return Response({
                'error': 'Access gate is not deleted and cannot be restored'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        instance.deleted_at = None
        instance.save(update_fields=['deleted_at'])
        
        serializer = AccessGatesSerializer(instance)
        return Response({
            'message': 'Access gate restored successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    

# System Settings Views
class DatabaseBackupView(APIView):
    permission_classes = [IsAdministrator]

    def post(self, request):
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        backup_dir = os.path.join(os.path.dirname(__file__), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

        env = os.environ.copy()
        env['PGPASSWORD'] = db_password  # Set password

        try:
            subprocess.run(
                ["pg_dump", "-U", db_user, db_name, "-f", backup_file],
                check=True, env=env
            )
            return Response({"status": "success", "backup_file": backup_file}, status=status.HTTP_200_OK)
        except subprocess.CalledProcessError as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DatabaseRestoreView(APIView):
    permission_classes = [IsAdministrator]

    def post(self, request, backup_filename):
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        backup_dir = os.path.join(os.path.dirname(__file__), "backups")
        backup_path = os.path.join(backup_dir, backup_filename)
        if not os.path.exists(backup_path):
            return Response({"status": "error", "message": "Backup not found"}, status=status.HTTP_404_NOT_FOUND)

        env = os.environ.copy()
        env['PGPASSWORD'] = db_password  # Set password

        try:
            subprocess.run(
                ["psql", "-U", db_user, "-d", db_name, "-f", backup_path],
                check=True, env=env
            )
            return Response({"status": "success", "message": "Database restored"}, status=status.HTTP_200_OK)
        except subprocess.CalledProcessError as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DatabaseBackupListView(APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        backup_dir = os.path.join(os.path.dirname(__file__), "backups")
        if not os.path.exists(backup_dir):
            return Response({"backups": []}, status=status.HTTP_200_OK)
        
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.sql')]
        return Response({"backups": backups}, status=status.HTTP_200_OK)