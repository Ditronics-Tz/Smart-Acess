from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include("authenication.urls")),
    path('', include('adminstrator.urls')),
    path('api/students/', include('students.urls')),
    path('api/cards/', include('cardmanage.urls')),  # Add this line
]
