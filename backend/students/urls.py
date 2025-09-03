
# In your urls.py file, you would have:
from rest_framework import routers
from .views import StudentViewSet # Assuming this file is named api.py

router = routers.DefaultRouter()
router.register(r'students', StudentViewSet)

urlpatterns = router.urls