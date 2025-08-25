from rest_framework import generics, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import SecurityPersonnel
from .serializers import SecurityPersonnelSerializer
from .permissions import IsAdministrator

class SecurityPersonnelPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class SecurityPersonnelCreateView(generics.CreateAPIView):
	queryset = SecurityPersonnel.objects.all()
	serializer_class = SecurityPersonnelSerializer
	permission_classes = [IsAdministrator]

class SecurityPersonnelListView(generics.ListAPIView): #list of secuirty perosnnel w filter
    queryset = SecurityPersonnel.objects.all()
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
