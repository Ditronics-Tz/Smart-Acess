from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    # Dashboard and overview
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    
    # Detailed analytics endpoints
    path('analytics/cards/', views.card_analytics, name='card_analytics'),
    path('analytics/verifications/', views.verification_analytics, name='verification_analytics'),
    path('analytics/demographics/', views.user_demographics, name='user_demographics'),
    
    # System health and monitoring
    path('system/health/', views.system_health_report, name='system_health_report'),
    
    # Comprehensive reporting
    path('reports/comprehensive/', views.comprehensive_report, name='comprehensive_report'),
    
    # Alert management
    path('alerts/', views.system_alerts, name='system_alerts'),
    path('alerts/<uuid:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
    path('alerts/<uuid:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    
    # Historical data and snapshots
    path('analytics/historical/', views.historical_analytics, name='historical_analytics'),
    path('snapshots/generate/', views.generate_snapshot, name='generate_snapshot'),
]