from rest_framework import serializers
from .models import Staff

class StaffSerializer(serializers.ModelSerializer):
	class Meta:
		model = Staff
		fields = [
			'staff_uuid', 'surname', 'first_name', 'middle_name', 'mobile_phone',
			'staff_number', 'department', 'position', 'employment_status', 'is_active',
			'created_at', 'updated_at'
		]
