from rest_framework import routers
from django.urls import path
from .views import CardViewSet, verify_student, verify_staff, verify_security

router = routers.DefaultRouter()
router.register(r'', CardViewSet, basename='card')

urlpatterns = [
    path('verify/student/<uuid:student_uuid>/', verify_student, name='verify-student'),
    path('verify/staff/<uuid:staff_uuid>/', verify_staff, name='verify-staff'),
    path('verify/security/<uuid:security_uuid>/', verify_security, name='verify-security'),
] + router.urls