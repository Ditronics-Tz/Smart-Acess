from django.urls import path
from .views import SecurityPersonnelCreateView, SecurityPersonnelListView, SecurityPersonnelDetailView, SecurityPersonnelUpdateView, SecurityPersonnelDeleteView, SecurityPersonnelRestoreView

urlpatterns = [
    path('api/administrator/security-personnel/', SecurityPersonnelListView.as_view(), name='security-personnel-list'),  # GET
    path('api/administrator/security-personnel/create/', SecurityPersonnelCreateView.as_view(), name='security-personnel-create'),  # POST
    path('api/administrator/security-personnel/<uuid:security_id>/', SecurityPersonnelDetailView.as_view(), name='security-personnel-detail'),  # GET by ID
    path('api/administrator/security-personnel/<uuid:security_id>/update/', SecurityPersonnelUpdateView.as_view(), name='security-personnel-update'),  # PUT & PATCH by ID
    path('api/administrator/security-personnel/<uuid:security_id>/delete/', SecurityPersonnelDeleteView.as_view(), name='security-personnel-delete'),  # DELETE by ID (soft delete)
    path('api/administrator/security-personnel/<uuid:security_id>/restore/', SecurityPersonnelRestoreView.as_view(), name='security-personnel-restore'),  # POST by ID (restore)
]