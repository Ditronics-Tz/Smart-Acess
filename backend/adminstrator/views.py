from rest_framework import generics
from .models import SecurityPersonnel
from .serializers import SecurityPersonnelSerializer
from .permissions import IsAdministrator

class SecurityPersonnelCreateView(generics.CreateAPIView):
	queryset = SecurityPersonnel.objects.all()
	serializer_class = SecurityPersonnelSerializer
	permission_classes = [IsAdministrator]
