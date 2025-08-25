from django.urls import path
from .views import SecurityPersonnelCreateView, SecurityPersonnelListView, SecurityPersonnelDetailView, SecurityPersonnelUpdateView

urlpatterns = [
    path('api/administrator/security-personnel/', SecurityPersonnelListView.as_view(), name='security-personnel-list'),  # GET
    path('api/administrator/security-personnel/create/', SecurityPersonnelCreateView.as_view(), name='security-personnel-create'),  # POST
    path('api/administrator/security-personnel/<uuid:security_id>/', SecurityPersonnelDetailView.as_view(), name='security-personnel-detail'),  # GET by ID
    path('api/administrator/security-personnel/<uuid:security_id>/update/', SecurityPersonnelUpdateView.as_view(), name='security-personnel-update'),  # PUT by ID
]