from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Staff

class StaffModelTest(TestCase):
    def setUp(self):
        self.staff = Staff.objects.create(
            surname="Doe",
            first_name="John",
            staff_number="STF001",
            department="IT Department",
            position="System Administrator"
        )

    def test_staff_creation(self):
        self.assertEqual(self.staff.surname, "Doe")
        self.assertEqual(self.staff.first_name, "John")
        self.assertEqual(self.staff.staff_number, "STF001")
        self.assertTrue(self.staff.is_active)
        self.assertEqual(str(self.staff), "John Doe (STF001)")

    def test_staff_uuid_is_unique(self):
        staff2 = Staff.objects.create(
            surname="Smith",
            first_name="Jane",
            staff_number="STF002",
            department="HR",
            position="HR Manager"
        )
        self.assertNotEqual(self.staff.staff_uuid, staff2.staff_uuid)

class StaffAPITest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            user_type='administrator'
        )
        self.staff_data = {
            'surname': 'Johnson',
            'first_name': 'Mike',
            'staff_number': 'STF003',
            'department': 'Finance',
            'position': 'Accountant'
        }

    def test_create_staff_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/staff/', self.staff_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Staff.objects.count(), 1)
        self.assertEqual(Staff.objects.get().staff_number, 'STF003')

    def test_list_staff_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/staff/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_number_uniqueness(self):
        Staff.objects.create(**self.staff_data)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/staff/', self.staff_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
