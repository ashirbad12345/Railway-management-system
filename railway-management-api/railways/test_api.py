from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Train


class RailwayAPITests(APITestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="rider", password="strong-password-123")
		self.train = Train.objects.create(
			train_number="TEST001",
			name="Morning Express",
			source="Delhi",
			destination="Mumbai",
			total_seats=2,
			available_seats=2,
		)

	def test_register_and_login(self):
		response = self.client.post("/api/auth/register/", {"username": "new-user", "password": "strong-password-123"})
		self.assertEqual(response.status_code, 201)
		response = self.client.post("/api/auth/login/", {"username": "rider", "password": "strong-password-123"})
		self.assertEqual(response.status_code, 200)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)

	def test_search_returns_train_availability(self):
		response = self.client.get("/api/trains/?source=Delhi&destination=Mumbai")
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data[0]["available_seats"], 2)

	def test_booking_decrements_availability(self):
		self.client.force_authenticate(self.user)
		response = self.client.post(f"/api/trains/{self.train.id}/bookings/", {"seats": 1})
		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["status"], "CONFIRMED")
		self.train.refresh_from_db()
		self.assertEqual(self.train.available_seats, 1)

	def test_booking_cannot_exceed_availability(self):
		self.client.force_authenticate(self.user)
		response = self.client.post(f"/api/trains/{self.train.id}/bookings/", {"seats": 3})
		self.assertEqual(response.status_code, 409)

	def test_booking_detail_is_private_to_owner(self):
		self.client.force_authenticate(self.user)
		booking_response = self.client.post(f"/api/trains/{self.train.id}/bookings/", {"seats": 1})
		other_user = get_user_model().objects.create_user(username="other", password="strong-password-123")
		self.client.force_authenticate(other_user)
		response = self.client.get(f"/api/bookings/{booking_response.data['id']}/")
		self.assertEqual(response.status_code, 404)
