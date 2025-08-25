from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
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

class SecurityPersonnelListView(generics.ListAPIView):
    queryset = SecurityPersonnel.objects.all()
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAdministrator]
    pagination_class = SecurityPersonnelPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['full_name', 'employee_id', 'badge_number']
    ordering_fields = ['full_name', 'employee_id', 'badge_number', 'hire_date', 'created_at']
    ordering = ['-created_at']

class SecurityPersonnelDetailView(generics.RetrieveAPIView):
    queryset = SecurityPersonnel.objects.all()
    serializer_class = SecurityPersonnelSerializer
    permission_classes = [IsAdministrator]
    lookup_field = 'security_id'
