from rest_framework import routers
from django.urls import path
from .views import StudentViewSet

# Create a router without a root API view
router = routers.DefaultRouter()
# Register with empty prefix since we already included it with the api/students/ prefix
router.register(r'', StudentViewSet, basename='student')

# The urlpatterns are what Django's URL resolver uses to find the correct view.
urlpatterns = router.urls