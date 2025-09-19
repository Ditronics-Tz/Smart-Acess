from django.shortcuts import render
from .permissions import IsAdministrator, CanManageAccess, IsAccessControlDevice, CanViewAccessLogs
from .models import AccessLog
from .serializers import (
    AccessRequestSerializer, AccessResponseSerializer, AccessLogSerializer,
    AccessLogListSerializer, AccessStatisticsSerializer, StudentInfoSerializer
)
from cardmanage.models import Card
from students.models import Student
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)


class AccessControlViewSet(viewsets.ModelViewSet):
    """
    API endpoint for access control and logging.
    
    Permissions:
    - Administrators: Full access to all operations
    - Registration Officers: Can view logs and statistics
    - Access Control Devices: Can use check_access endpoint
    """
    queryset = AccessLog.objects.all().select_related('card__student').order_by('-timestamp')
    serializer_class = AccessLogSerializer
    permission_classes = [CanViewAccessLogs]
    lookup_field = 'log_uuid'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'access_status', 'denial_reason', 'access_location', 
        'device_identifier', 'card__is_active'
    ]
    search_fields = [
        'rfid_number', 'card__student__first_name', 'card__student__surname',
        'card__student__registration_number', 'access_location'
    ]
    ordering_fields = ['timestamp', 'access_status', 'rfid_number']
    ordering = ['-timestamp']

    def get_serializer_class(self):
        """
        Return different serializers based on action
        """
        if self.action == 'list':
            return AccessLogListSerializer
        elif self.action == 'check_access':
            return AccessRequestSerializer
        elif self.action == 'statistics':
            return AccessStatisticsSerializer
        return AccessLogSerializer

    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        """
        if self.action == 'check_access':
            # Allow access control devices to use this endpoint
            permission_classes = [IsAccessControlDevice]
        elif self.action in ['destroy', 'create', 'update', 'partial_update']:
            # Only administrators can modify logs
            permission_classes = [IsAdministrator]
        else:
            # View access logs and statistics
            permission_classes = [CanViewAccessLogs]
            
        return [permission() for permission in permission_classes]

    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def list(self, request, *args, **kwargs):
        """
        List access logs with pagination and filtering.
        Available to administrators and registration officers.
        """
        response = super().list(request, *args, **kwargs)
        
        # Add summary statistics to response
        if hasattr(response, 'data') and isinstance(response.data, dict):
            total_logs = AccessLog.objects.count()
            granted_today = AccessLog.objects.filter(
                access_status='granted',
                timestamp__date=timezone.now().date()
            ).count()
            denied_today = AccessLog.objects.filter(
                access_status='denied',
                timestamp__date=timezone.now().date()
            ).count()
            
            response.data['summary'] = {
                'total_logs': total_logs,
                'granted_today': granted_today,
                'denied_today': denied_today,
                'total_today': granted_today + denied_today
            }
            
            response.data['user_permissions'] = {
                'current_user': request.user.username,
                'user_type': request.user.user_type,
                'can_view_details': True,
                'can_delete': request.user.user_type == 'administrator'
            }
        
        return response

    @action(
        detail=False,
        methods=['post'],
        url_path='check-access',
        permission_classes=[IsAccessControlDevice]
    )
    def check_access(self, request):
        """
        SIMPLE & FAST RFID access control endpoint.
        Target response time: <20ms
        """
        start_time = timezone.now()
        
        # Simple validation
        rfid_number = request.data.get('rfid_number', '').strip()
        if not rfid_number:
            return Response({
                'access_granted': False,
                'message': 'Invalid RFID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_granted = False
        message = "Access denied"
        student_name = None
        denial_reason = None
        
        try:
            # SIMPLE: One optimized query
            card = Card.objects.select_related('student').filter(
                rfid_number=rfid_number
            ).only(
                'is_active', 'expiry_date',
                'student__first_name', 'student__surname', 
                'student__is_active', 'student__registration_number',
                'student__department', 'student__student_status',
                'student__email', 'student__phone_number'
            ).first()
            
            if not card:
                denial_reason = 'invalid_rfid'
                message = "Invalid RFID"
            elif not card.is_active:
                denial_reason = 'card_inactive'
                message = "Card inactive"
            elif card.expiry_date and card.expiry_date < timezone.now():
                denial_reason = 'card_expired'
                message = "Card expired"
            elif not card.student.is_active:
                denial_reason = 'student_inactive'
                message = "Student inactive"
            else:
                access_granted = True
                message = "Access granted"
                student_name = f"{card.student.first_name} {card.student.surname}"
        
        except Exception:
            denial_reason = 'system_error'
            message = "System error"
        
        # Calculate response time
        response_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
        
        # SIMPLE: Log without blocking (minimal fields)
        try:
            AccessLog.objects.create(
                rfid_number=rfid_number,
                card=card if card else None,
                access_status='granted' if access_granted else 'denied',
                denial_reason=denial_reason,
                timestamp=start_time,
                response_time_ms=response_time_ms
            )
        except:
            pass  # Don't fail access check if logging fails
        
        # SIMPLE: Minimal response
        response_data = {
            'access_granted': access_granted,
            'message': message,
            'response_time': response_time_ms
        }
        
        if access_granted and student_name and card:
            response_data['student'] = {
                'name': student_name,
                'first_name': card.student.first_name,
                'surname': card.student.surname,
                'registration_number': card.student.registration_number,
                'department': card.student.department,
                'status': card.student.student_status,
                'email': getattr(card.student, 'email', None),
                'phone': getattr(card.student, 'phone_number', None)
            }
        
        return Response(response_data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path='statistics',
        permission_classes=[CanViewAccessLogs]
    )
    def access_statistics(self, request):
        """
        Get comprehensive access control statistics.
        Available to administrators and registration officers.
        """
        # Get date range parameters
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Basic statistics
        total_attempts = AccessLog.objects.count()
        granted_access = AccessLog.objects.filter(access_status='granted').count()
        denied_access = AccessLog.objects.filter(access_status='denied').count()
        success_rate = round((granted_access / total_attempts * 100), 2) if total_attempts > 0 else 0
        
        # Time-based statistics
        attempts_today = AccessLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        attempts_this_week = AccessLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        attempts_this_month = AccessLog.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Denial reasons breakdown
        denial_reasons = dict(
            AccessLog.objects.filter(
                access_status='denied',
                timestamp__gte=start_date
            ).values('denial_reason').annotate(
                count=Count('id')
            ).values_list('denial_reason', 'count')
        )
        
        # Top locations
        top_locations = list(
            AccessLog.objects.filter(
                timestamp__gte=start_date,
                access_location__isnull=False
            ).exclude(
                access_location=''
            ).values('access_location').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )
        
        # Recent activity (last 10 attempts)
        recent_activity = AccessLog.objects.select_related(
            'card__student'
        ).order_by('-timestamp')[:10]
        recent_serializer = AccessLogListSerializer(recent_activity, many=True)
        
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.info(f"Access statistics requested by {user_info}")
        
        return Response({
            'summary': {
                'total_attempts': total_attempts,
                'granted_access': granted_access,
                'denied_access': denied_access,
                'success_rate': success_rate,
                'attempts_today': attempts_today,
                'attempts_this_week': attempts_this_week,
                'attempts_this_month': attempts_this_month
            },
            'denial_reasons': denial_reasons,
            'top_locations': top_locations,
            'recent_activity': recent_serializer.data,
            'parameters': {
                'days_analyzed': days,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'generated_at': timezone.now().isoformat(),
            'generated_by': user_info
        }, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        url_path='recent-activity',
        permission_classes=[CanViewAccessLogs]
    )
    def recent_activity(self, request):
        """
        Get recent access activity.
        Available to administrators and registration officers.
        """
        limit = int(request.query_params.get('limit', 20))
        hours = int(request.query_params.get('hours', 24))
        
        since = timezone.now() - timedelta(hours=hours)
        
        recent_logs = AccessLog.objects.select_related(
            'card__student'
        ).filter(
            timestamp__gte=since
        ).order_by('-timestamp')[:limit]
        
        serializer = AccessLogListSerializer(recent_logs, many=True)
        
        return Response({
            'count': recent_logs.count(),
            'activity': serializer.data,
            'parameters': {
                'hours': hours,
                'limit': limit,
                'since': since.isoformat()
            },
            'generated_at': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete access log - Only available to Administrators.
        """
        user_info = f"{request.user.username} ({request.user.user_type})"
        logger.warning(f"Access log deletion initiated by {user_info}")
        
        instance = self.get_object()
        log_info = f"RFID: {instance.rfid_number}, Status: {instance.access_status}, Time: {instance.timestamp}"
        
        response = super().destroy(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            logger.warning(f"Access log {instance.log_uuid} deleted by {user_info} - {log_info}")
        
        return response
