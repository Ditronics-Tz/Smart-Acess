from django.shortcuts import render
from django.db.models import Count, Q, Avg, Sum, Max, Min
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Import models from different apps
from students.models import Student, StudentPhoto
from staff.models import Staff, StaffPhoto  
from cardmanage.models import Card, IDCardPrintLog, IDCardVerificationLog
from adminstrator.models import SecurityPersonnel, PhysicalLocations, AccessGates
from students.permissions import IsAdministrator

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAdministrator])
def dashboard_overview(request):
    """
    Main dashboard overview with key statistics
    """
    try:
        # Current date for filtering
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)
        
        # Basic counts
        total_students = Student.objects.filter(is_active=True).count()
        total_staff = Staff.objects.filter(is_active=True).count()
        total_security = SecurityPersonnel.objects.filter(is_active=True).count()
        total_cards = Card.objects.filter(is_active=True).count()
        
        # Card distribution
        card_distribution = {
            'student_cards': Card.objects.filter(card_type='student', is_active=True).count(),
            'staff_cards': Card.objects.filter(card_type='staff', is_active=True).count(),
            'security_cards': Card.objects.filter(card_type='security', is_active=True).count()
        }
        
        # Recent activity (last 7 days)
        recent_prints = IDCardPrintLog.objects.filter(
            printed_at__date__gte=seven_days_ago
        ).count()
        
        recent_verifications = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=seven_days_ago
        ).count()
        
        # Photo completion rate
        students_with_photos = Student.objects.filter(
            is_active=True,
            photo__photo__isnull=False
        ).count()
        
        staff_with_photos = Staff.objects.filter(
            is_active=True,
            photo__photo__isnull=False
        ).count()
        
        photo_completion = {
            'students': {
                'total': total_students,
                'with_photos': students_with_photos,
                'completion_rate': round((students_with_photos / total_students * 100) if total_students > 0 else 0, 2)
            },
            'staff': {
                'total': total_staff,
                'with_photos': staff_with_photos,
                'completion_rate': round((staff_with_photos / total_staff * 100) if total_staff > 0 else 0, 2)
            }
        }
        
        # System health
        active_gates = AccessGates.objects.filter(status='active', deleted_at__isnull=True).count()
        total_gates = AccessGates.objects.filter(deleted_at__isnull=True).count()
        
        response_data = {
            'success': True,
            'data': {
                'overview': {
                    'total_users': total_students + total_staff + total_security,
                    'total_students': total_students,
                    'total_staff': total_staff,
                    'total_security': total_security,
                    'total_cards': total_cards,
                    'active_cards': total_cards  # All counted cards are active
                },
                'card_distribution': card_distribution,
                'recent_activity': {
                    'card_prints_7_days': recent_prints,
                    'verifications_7_days': recent_verifications
                },
                'photo_completion': photo_completion,
                'system_health': {
                    'total_gates': total_gates,
                    'active_gates': active_gates,
                    'gate_uptime': round((active_gates / total_gates * 100) if total_gates > 0 else 0, 2)
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def card_analytics(request):
    """
    Detailed card analytics and statistics
    """
    try:
        # Get date range from query params
        days = int(request.GET.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Card issuance trends
        card_issuance_by_date = Card.objects.filter(
            issued_date__date__gte=start_date
        ).extra(
            select={'date': 'DATE(issued_date)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Card type distribution
        card_type_stats = Card.objects.filter(
            is_active=True
        ).values('card_type').annotate(
            count=Count('id')
        )
        
        # Print activity analysis
        print_activity = IDCardPrintLog.objects.filter(
            printed_at__date__gte=start_date
        ).extra(
            select={'date': 'DATE(printed_at)'}
        ).values('date').annotate(
            prints=Count('id')
        ).order_by('date')
        
        # Top printing users
        top_printers = IDCardPrintLog.objects.filter(
            printed_at__date__gte=start_date
        ).values('printed_by', 'user_type').annotate(
            print_count=Count('id')
        ).order_by('-print_count')[:10]
        
        # Department-wise card distribution (for students)
        student_dept_distribution = Card.objects.filter(
            card_type='student',
            is_active=True,
            student__isnull=False
        ).values('student__department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Staff department distribution
        staff_dept_distribution = Card.objects.filter(
            card_type='staff',
            is_active=True,
            staff__isnull=False
        ).values('staff__department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        response_data = {
            'success': True,
            'data': {
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': timezone.now().date().isoformat(),
                    'days': days
                },
                'issuance_trends': list(card_issuance_by_date),
                'card_type_distribution': list(card_type_stats),
                'print_activity': list(print_activity),
                'top_printers': list(top_printers),
                'department_distribution': {
                    'students': list(student_dept_distribution),
                    'staff': list(staff_dept_distribution)
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def verification_analytics(request):
    """
    Card verification and usage analytics
    """
    try:
        # Get date range
        days = int(request.GET.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Verification trends by date
        verification_trends = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=start_date
        ).extra(
            select={'date': 'DATE(verified_at)'}
        ).values('date').annotate(
            verifications=Count('id')
        ).order_by('date')
        
        # Verification by source
        verification_sources = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=start_date
        ).values('verification_source').annotate(
            count=Count('id')
        )
        
        # Hourly verification patterns
        hourly_patterns = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=start_date
        ).extra(
            select={'hour': 'EXTRACT(hour FROM verified_at)'}
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        # Most verified users (students/staff)
        most_verified_students = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=start_date,
            student__isnull=False
        ).values(
            'student__registration_number',
            'student__first_name',
            'student__surname'
        ).annotate(
            verification_count=Count('id')
        ).order_by('-verification_count')[:10]
        
        most_verified_staff = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=start_date,
            staff__isnull=False
        ).values(
            'staff__staff_number',
            'staff__first_name',
            'staff__surname'
        ).annotate(
            verification_count=Count('id')
        ).order_by('-verification_count')[:10]
        
        # Average verifications per day
        total_verifications = IDCardVerificationLog.objects.filter(
            verified_at__date__gte=start_date
        ).count()
        
        avg_verifications_per_day = total_verifications / days if days > 0 else 0
        
        response_data = {
            'success': True,
            'data': {
                'summary': {
                    'total_verifications': total_verifications,
                    'avg_per_day': round(avg_verifications_per_day, 2),
                    'date_range_days': days
                },
                'trends': list(verification_trends),
                'verification_sources': list(verification_sources),
                'hourly_patterns': list(hourly_patterns),
                'top_verified_users': {
                    'students': list(most_verified_students),
                    'staff': list(most_verified_staff)
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def user_demographics(request):
    """
    User demographics and population analytics
    """
    try:
        # Student demographics
        student_by_status = Student.objects.filter(
            is_active=True
        ).values('academic_year_status').annotate(
            count=Count('id')
        )
        
        student_by_department = Student.objects.filter(
            is_active=True
        ).values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Staff demographics
        staff_by_status = Staff.objects.filter(
            is_active=True
        ).values('employment_status').annotate(
            count=Count('id')
        )
        
        staff_by_department = Staff.objects.filter(
            is_active=True
        ).values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Registration trends (students and staff over time)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        
        student_registration_trends = Student.objects.filter(
            created_at__date__gte=thirty_days_ago
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        staff_registration_trends = Staff.objects.filter(
            created_at__date__gte=thirty_days_ago
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Mobile phone completion rate
        students_with_phones = Student.objects.filter(
            is_active=True,
            mobile_phone__isnull=False,
            mobile_phone__gt=''
        ).count()
        
        staff_with_phones = Staff.objects.filter(
            is_active=True,
            mobile_phone__isnull=False,
            mobile_phone__gt=''
        ).count()
        
        total_students = Student.objects.filter(is_active=True).count()
        total_staff = Staff.objects.filter(is_active=True).count()
        
        response_data = {
            'success': True,
            'data': {
                'students': {
                    'total': total_students,
                    'by_status': list(student_by_status),
                    'by_department': list(student_by_department),
                    'registration_trends': list(student_registration_trends),
                    'phone_completion_rate': round((students_with_phones / total_students * 100) if total_students > 0 else 0, 2)
                },
                'staff': {
                    'total': total_staff,
                    'by_status': list(staff_by_status),
                    'by_department': list(staff_by_department),
                    'registration_trends': list(staff_registration_trends),
                    'phone_completion_rate': round((staff_with_phones / total_staff * 100) if total_staff > 0 else 0, 2)
                },
                'security_personnel': {
                    'total': SecurityPersonnel.objects.filter(is_active=True).count(),
                    'active': SecurityPersonnel.objects.filter(is_active=True, termination_date__isnull=True).count()
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def system_health_report(request):
    """
    System health and infrastructure status
    """
    try:
        # Gate status analysis
        gate_status_summary = AccessGates.objects.filter(
            deleted_at__isnull=True
        ).values('status').annotate(
            count=Count('id')
        )
        
        # Location-wise gate distribution
        gates_by_location = AccessGates.objects.filter(
            deleted_at__isnull=True
        ).select_related('location').values(
            'location__location_name',
            'location__location_type'
        ).annotate(
            gate_count=Count('id')
        ).order_by('-gate_count')
        
        # Physical locations summary
        locations_by_type = PhysicalLocations.objects.filter(
            deleted_at__isnull=True
        ).values('location_type').annotate(
            count=Count('id')
        )
        
        restricted_locations = PhysicalLocations.objects.filter(
            deleted_at__isnull=True,
            is_restricted=True
        ).count()
        
        total_locations = PhysicalLocations.objects.filter(
            deleted_at__isnull=True
        ).count()
        
        # Data integrity checks
        students_without_cards = Student.objects.filter(
            is_active=True,
            card__isnull=True
        ).count()
        
        staff_without_cards = Staff.objects.filter(
            is_active=True,
            card__isnull=True
        ).count()
        
        cards_without_photos = Card.objects.filter(
            is_active=True
        ).filter(
            Q(card_type='student', student__photo__isnull=True) |
            Q(card_type='staff', staff__photo__isnull=True)
        ).count()
        
        response_data = {
            'success': True,
            'data': {
                'infrastructure': {
                    'gates': {
                        'total': AccessGates.objects.filter(deleted_at__isnull=True).count(),
                        'status_summary': list(gate_status_summary),
                        'by_location': list(gates_by_location)
                    },
                    'locations': {
                        'total': total_locations,
                        'restricted': restricted_locations,
                        'by_type': list(locations_by_type)
                    }
                },
                'data_integrity': {
                    'students_without_cards': students_without_cards,
                    'staff_without_cards': staff_without_cards,
                    'cards_without_photos': cards_without_photos
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def comprehensive_report(request):
    """
    Comprehensive system report combining all analytics
    """
    try:
        # Get individual reports
        dashboard_data = dashboard_overview(request).data['data']
        card_data = card_analytics(request).data['data']
        verification_data = verification_analytics(request).data['data']
        demographics_data = user_demographics(request).data['data']
        health_data = system_health_report(request).data['data']
        
        # Calculate additional insights
        card_utilization_rate = (
            verification_data['summary']['total_verifications'] / 
            dashboard_data['overview']['total_cards']
        ) if dashboard_data['overview']['total_cards'] > 0 else 0
        
        response_data = {
            'success': True,
            'report_type': 'comprehensive',
            'data': {
                'executive_summary': {
                    'total_system_users': dashboard_data['overview']['total_users'],
                    'total_active_cards': dashboard_data['overview']['total_cards'],
                    'card_utilization_rate': round(card_utilization_rate, 2),
                    'system_health_score': health_data['infrastructure']['gates']['total'],
                    'data_completeness_score': round(
                        (dashboard_data['photo_completion']['students']['completion_rate'] + 
                         dashboard_data['photo_completion']['staff']['completion_rate']) / 2, 2
                    )
                },
                'dashboard_overview': dashboard_data,
                'card_analytics': card_data,
                'verification_analytics': verification_data,
                'user_demographics': demographics_data,
                'system_health': health_data
            },
            'generated_at': timezone.now().isoformat(),
            'report_version': '1.0'
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def system_alerts(request):
    """
    Get current system alerts and notifications
    """
    try:
        from .models import SystemAlert
        from .utils import check_system_alerts
        
        # Check for new alerts
        check_system_alerts()
        
        # Get active alerts
        active_alerts = SystemAlert.objects.filter(is_active=True).order_by('-created_at')
        
        # Get recently resolved alerts (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        resolved_alerts = SystemAlert.objects.filter(
            is_active=False,
            resolved_at__gte=seven_days_ago
        ).order_by('-resolved_at')[:10]
        
        # Alert summary by severity
        alert_summary = SystemAlert.objects.filter(
            is_active=True
        ).values('severity').annotate(
            count=Count('id')
        )
        
        active_alerts_data = []
        for alert in active_alerts:
            active_alerts_data.append({
                'id': str(alert.alert_id),
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'description': alert.description,
                'metric_value': alert.metric_value,
                'threshold_value': alert.threshold_value,
                'created_at': alert.created_at.isoformat(),
                'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'acknowledged_by': alert.acknowledged_by
            })
        
        resolved_alerts_data = []
        for alert in resolved_alerts:
            resolved_alerts_data.append({
                'id': str(alert.alert_id),
                'type': alert.alert_type,
                'severity': alert.severity,
                'title': alert.title,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            })
        
        response_data = {
            'success': True,
            'data': {
                'active_alerts': active_alerts_data,
                'resolved_alerts': resolved_alerts_data,
                'summary': {
                    'total_active': len(active_alerts_data),
                    'by_severity': list(alert_summary)
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdministrator])
def acknowledge_alert(request, alert_id):
    """
    Acknowledge a system alert
    """
    try:
        from .models import SystemAlert
        
        alert = SystemAlert.objects.get(alert_id=alert_id, is_active=True)
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user.username
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alert acknowledged successfully',
            'alert_id': str(alert_id)
        }, status=status.HTTP_200_OK)
        
    except SystemAlert.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Alert not found or already resolved'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdministrator])
def resolve_alert(request, alert_id):
    """
    Resolve a system alert
    """
    try:
        from .models import SystemAlert
        
        alert = SystemAlert.objects.get(alert_id=alert_id, is_active=True)
        alert.is_active = False
        alert.resolved_at = timezone.now()
        alert.save()
        
        return Response({
            'success': True,
            'message': 'Alert resolved successfully',
            'alert_id': str(alert_id)
        }, status=status.HTTP_200_OK)
        
    except SystemAlert.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Alert not found or resolved'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdministrator])
def historical_analytics(request):
    """
    Get historical analytics snapshots
    """
    try:
        from .models import AnalyticsSnapshot
        
        # Get query parameters
        report_type = request.GET.get('type', 'daily')
        days = int(request.GET.get('days', 30))
        
        start_date = timezone.now().date() - timedelta(days=days)
        
        snapshots = AnalyticsSnapshot.objects.filter(
            report_type=report_type,
            snapshot_date__date__gte=start_date
        ).order_by('snapshot_date')
        
        snapshots_data = []
        for snapshot in snapshots:
            snapshots_data.append({
                'date': snapshot.snapshot_date.date().isoformat(),
                'total_users': snapshot.total_users,
                'total_students': snapshot.total_students,
                'total_staff': snapshot.total_staff,
                'total_cards': snapshot.total_cards,
                'daily_verifications': snapshot.daily_verifications,
                'student_photo_completion': snapshot.student_photo_completion_rate,
                'staff_photo_completion': snapshot.staff_photo_completion_rate
            })
        
        # Calculate trends
        if len(snapshots_data) >= 2:
            latest = snapshots_data[-1]
            previous = snapshots_data[-2]
            
            trends = {
                'user_growth': latest['total_users'] - previous['total_users'],
                'card_growth': latest['total_cards'] - previous['total_cards'],
                'verification_change': latest['daily_verifications'] - previous['daily_verifications']
            }
        else:
            trends = None
        
        response_data = {
            'success': True,
            'data': {
                'snapshots': snapshots_data,
                'trends': trends,
                'parameters': {
                    'report_type': report_type,
                    'days': days,
                    'total_snapshots': len(snapshots_data)
                }
            },
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdministrator])
def generate_snapshot(request):
    """
    Generate a new analytics snapshot
    """
    try:
        from .utils import create_analytics_snapshot
        
        report_type = request.data.get('type', 'manual')
        snapshot = create_analytics_snapshot(report_type)
        
        return Response({
            'success': True,
            'message': 'Analytics snapshot created successfully',
            'snapshot_id': str(snapshot.snapshot_id),
            'created_at': snapshot.created_at.isoformat()
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
