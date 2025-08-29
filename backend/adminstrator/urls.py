from django.urls import path
from .views import (
    SecurityPersonnelCreateView, SecurityPersonnelListView, SecurityPersonnelDetailView, 
    SecurityPersonnelUpdateView, SecurityPersonnelDeleteView, SecurityPersonnelRestoreView,
    PhysicalLocationsCreateView, PhysicalLocationsListView, PhysicalLocationsDetailView,
    PhysicalLocationsUpdateView, PhysicalLocationsDeleteView, PhysicalLocationsRestoreView,
    AccessGatesCreateView, AccessGatesListView, AccessGatesDetailView,
    AccessGatesUpdateView, AccessGatesDeleteView, AccessGatesRestoreView
)

urlpatterns = [
    # Security Personnel URLs
    path('api/administrator/security-personnel/', SecurityPersonnelListView.as_view(), name='security-personnel-list'),  # GET
    path('api/administrator/security-personnel/create/', SecurityPersonnelCreateView.as_view(), name='security-personnel-create'),  # POST
    path('api/administrator/security-personnel/<uuid:security_id>/', SecurityPersonnelDetailView.as_view(), name='security-personnel-detail'),  # GET by ID
    path('api/administrator/security-personnel/<uuid:security_id>/update/', SecurityPersonnelUpdateView.as_view(), name='security-personnel-update'),  # PUT & PATCH by ID
    path('api/administrator/security-personnel/<uuid:security_id>/delete/', SecurityPersonnelDeleteView.as_view(), name='security-personnel-delete'),  # DELETE by ID (soft delete)
    path('api/administrator/security-personnel/<uuid:security_id>/restore/', SecurityPersonnelRestoreView.as_view(), name='security-personnel-restore'),  # POST by ID (restore)

    # Physical Locations URLs
    path('api/administrator/physical-locations/', PhysicalLocationsListView.as_view(), name='physical-locations-list'),  # GET
    path('api/administrator/physical-locations/create/', PhysicalLocationsCreateView.as_view(), name='physical-locations-create'),  # POST
    path('api/administrator/physical-locations/<uuid:location_id>/', PhysicalLocationsDetailView.as_view(), name='physical-locations-detail'),  # GET by ID
    path('api/administrator/physical-locations/<uuid:location_id>/update/', PhysicalLocationsUpdateView.as_view(), name='physical-locations-update'),  # PUT & PATCH by ID
    path('api/administrator/physical-locations/<uuid:location_id>/delete/', PhysicalLocationsDeleteView.as_view(), name='physical-locations-delete'),  # DELETE by ID (soft delete)
    path('api/administrator/physical-locations/<uuid:location_id>/restore/', PhysicalLocationsRestoreView.as_view(), name='physical-locations-restore'),  # POST by ID (restore)

    # Access Gates URLs
    path('api/administrator/access-gates/', AccessGatesListView.as_view(), name='access-gates-list'),  # GET
    path('api/administrator/access-gates/create/', AccessGatesCreateView.as_view(), name='access-gates-create'),  # POST
    path('api/administrator/access-gates/<uuid:gate_id>/', AccessGatesDetailView.as_view(), name='access-gates-detail'),  # GET by ID
    path('api/administrator/access-gates/<uuid:gate_id>/update/', AccessGatesUpdateView.as_view(), name='access-gates-update'),  # PUT & PATCH by ID
    path('api/administrator/access-gates/<uuid:gate_id>/delete/', AccessGatesDeleteView.as_view(), name='access-gates-delete'),  # DELETE by ID (soft delete)
    path('api/administrator/access-gates/<uuid:gate_id>/restore/', AccessGatesRestoreView.as_view(), name='access-gates-restore'),
]