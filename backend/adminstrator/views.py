from rest_framework import generics
from .models import SecurityPersonnel
from .serializers import SecurityPersonnelSerializer

class SecurityPersonnelCreateView(generics.CreateAPIView):
	queryset = SecurityPersonnel.objects.all()
	serializer_class = SecurityPersonnelSerializer
