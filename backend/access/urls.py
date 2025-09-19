from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'logs', views.AccessControlViewSet, basename='access-logs')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Simple access grant endpoint
    path('grant/', views.AccessControlViewSet.as_view({'post': 'check_access'}), name='access-grant'),
]

# URL patterns will be:
# POST /api/access/grant/ - Main RFID access control endpoint (SIMPLIFIED)
# GET /api/access/logs/ - List access logs
# GET /api/access/logs/{log_uuid}/ - Get specific access log
# DELETE /api/access/logs/{log_uuid}/ - Delete access log (admin only)
# POST /api/access/logs/check-access/ - Alternative access endpoint (still works)
# GET /api/access/logs/statistics/ - Get access statistics
# GET /api/access/logs/recent-activity/ - Get recent access activity