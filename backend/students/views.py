from .permissions import IsAdministrator
from .models import Student
from .serializers import StudentSerializer
from rest_framework import viewsets


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed or edited.
    """
    queryset = Student.objects.filter(is_active=True).order_by('surname', 'first_name')
    serializer_class = StudentSerializer

    permission_classes = [IsAdministrator]

    lookup_field = 'student_uuid'
