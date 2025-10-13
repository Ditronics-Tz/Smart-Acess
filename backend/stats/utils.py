from django.utils import timezone
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta
import hashlib
import json

from .models import AnalyticsSnapshot, SystemAlert, ReportCache
from students.models import Student
from staff.models import Staff
from cardmanage.models import Card, IDCardVerificationLog
from adminstrator.models import SecurityPersonnel, AccessGates


def generate_cache_key(endpoint, params=None):
    """
    Generate a unique cache key for API responses
    """
    cache_data = f"{endpoint}_{params or ''}_{timezone.now().date()}"
    return hashlib.md5(cache_data.encode()).hexdigest()


def get_or_create_cached_report(cache_key, generator_func, ttl_minutes=30):
    """
    Get cached report or generate new one
    """
    try:
        cache_entry = ReportCache.objects.get(cache_key=cache_key)
        if not cache_entry.is_expired():
            return cache_entry.report_data
        else:
            cache_entry.delete()
    except ReportCache.DoesNotExist:
        pass
    
    # Generate new report
    report_data = generator_func()
    
    # Cache the report
    ReportCache.objects.create(
        cache_key=cache_key,
        report_data=report_data,
        expires_at=timezone.now() + timedelta(minutes=ttl_minutes)
    )
    
    return report_data


def create_analytics_snapshot(report_type='daily'):
    """
    Create a snapshot of current system analytics
    """
    # Calculate metrics
    total_students = Student.objects.filter(is_active=True).count()
    total_staff = Staff.objects.filter(is_active=True).count()
    total_security = SecurityPersonnel.objects.filter(is_active=True).count()
    total_cards = Card.objects.filter(is_active=True).count()
    
    # Activity metrics (last 24 hours)
    yesterday = timezone.now() - timedelta(days=1)
    daily_verifications = IDCardVerificationLog.objects.filter(
        verified_at__gte=yesterday
    ).count()
    
    # Photo completion rates
    students_with_photos = Student.objects.filter(
        is_active=True,
        photo__photo__isnull=False
    ).count()
    
    staff_with_photos = Staff.objects.filter(
        is_active=True,
        photo__photo__isnull=False
    ).count()
    
    student_photo_rate = (students_with_photos / total_students * 100) if total_students > 0 else 0
    staff_photo_rate = (staff_with_photos / total_staff * 100) if total_staff > 0 else 0
    
    # System health
    active_gates = AccessGates.objects.filter(
        status='active',
        deleted_at__isnull=True
    ).count()
    total_gates = AccessGates.objects.filter(deleted_at__isnull=True).count()
    
    # Create snapshot
    snapshot = AnalyticsSnapshot.objects.create(
        report_type=report_type,
        total_users=total_students + total_staff + total_security,
        total_students=total_students,
        total_staff=total_staff,
        total_security=total_security,
        total_cards=total_cards,
        active_cards=total_cards,
        daily_verifications=daily_verifications,
        active_gates=active_gates,
        total_gates=total_gates,
        student_photo_completion_rate=student_photo_rate,
        staff_photo_completion_rate=staff_photo_rate
    )
    
    return snapshot


def check_system_alerts():
    """
    Check system for potential issues and create alerts
    """
    alerts_created = 0
    
    # Check photo completion rates
    total_students = Student.objects.filter(is_active=True).count()
    students_with_photos = Student.objects.filter(
        is_active=True,
        photo__photo__isnull=False
    ).count()
    
    if total_students > 0:
        completion_rate = (students_with_photos / total_students) * 100
        if completion_rate < 50:  # Less than 50% completion
            SystemAlert.objects.get_or_create(
                alert_type='low_photo_completion',
                is_active=True,
                defaults={
                    'severity': 'medium',
                    'title': 'Low Student Photo Completion Rate',
                    'description': f'Only {completion_rate:.1f}% of students have uploaded photos.',
                    'metric_value': completion_rate,
                    'threshold_value': 50.0
                }
            )
            alerts_created += 1
    
    # Check for offline gates
    offline_gates = AccessGates.objects.filter(
        status__in=['inactive', 'error', 'maintenance'],
        deleted_at__isnull=True
    ).count()
    
    if offline_gates > 0:
        SystemAlert.objects.get_or_create(
            alert_type='gate_offline',
            is_active=True,
            defaults={
                'severity': 'high' if offline_gates > 2 else 'medium',
                'title': f'{offline_gates} Access Gate(s) Offline',
                'description': f'{offline_gates} access gates are currently offline or in maintenance mode.',
                'metric_value': float(offline_gates)
            }
        )
        alerts_created += 1
    
    # Check data integrity - students without cards
    students_without_cards = Student.objects.filter(
        is_active=True,
        card__isnull=True
    ).count()
    
    if students_without_cards > 10:  # More than 10 students without cards
        SystemAlert.objects.get_or_create(
            alert_type='data_integrity',
            is_active=True,
            defaults={
                'severity': 'medium',
                'title': 'Students Without ID Cards',
                'description': f'{students_without_cards} active students do not have ID cards assigned.',
                'metric_value': float(students_without_cards)
            }
        )
        alerts_created += 1
    
    return alerts_created


def clean_expired_cache():
    """
    Remove expired cache entries
    """
    expired_count = ReportCache.objects.filter(
        expires_at__lt=timezone.now()
    ).count()
    
    ReportCache.objects.filter(
        expires_at__lt=timezone.now()
    ).delete()
    
    return expired_count


def get_trending_data(model, date_field, days=30):
    """
    Get trending data for a model over specified days
    """
    start_date = timezone.now().date() - timedelta(days=days)
    
    return model.objects.filter(
        **{f"{date_field}__date__gte": start_date}
    ).extra(
        select={'date': f'DATE({date_field})'}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')


def calculate_growth_rate(current_count, previous_count):
    """
    Calculate percentage growth rate
    """
    if previous_count == 0:
        return 100.0 if current_count > 0 else 0.0
    
    return ((current_count - previous_count) / previous_count) * 100