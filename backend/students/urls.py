from rest_framework import routers

from .views import StudentViewSet

# The DefaultRouter automatically creates the API root view and the URLs for our ViewSet.
router = routers.DefaultRouter()
router.register(r'students', StudentViewSet, basename='student')

# The urlpatterns are what Django's URL resolver uses to find the correct view.
urlpatterns = router.urls