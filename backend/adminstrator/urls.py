from django.urls import path
from .views import SecurityPersonnelCreateView

urlpatterns = [
    path('api/administrator/security-personnel/', SecurityPersonnelCreateView.as_view(), name='security-personnel-create'),
]
