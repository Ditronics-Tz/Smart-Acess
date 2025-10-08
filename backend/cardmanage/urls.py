from rest_framework import routers
from django.urls import path
from .views import CardViewSet, verify_student

# Create a router
router = routers.DefaultRouter()
# Register with empty prefix since we already included it with the api/cards/ prefix
router.register(r'', CardViewSet, basename='card')

# The urlpatterns are what Django's URL resolver uses to find the correct view.
urlpatterns = [
    path('verify/<uuid:student_uuid>/', verify_student, name='verify-student'),
] + router.urls