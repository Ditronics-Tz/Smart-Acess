from rest_framework import serializers
from  .models import Student


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        # The 'read_only_fields' 
        read_only_fields = ['id', 'student_uuid', 'created_at', 'updated_at']
