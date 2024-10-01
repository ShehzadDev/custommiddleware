from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserAuthTests(TestCase):
    def test_register_view(self):
        response = self.client.post(
            reverse("register"),
            {"email": "test@django.com", "password": "password", "role": "gold"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="test@django.com").exists())

    def test_login_view(self):
        user = User.objects.create_user(email="login@django.com", password="password")
        response = self.client.post(
            reverse("login"),
            {
                "email": user.email,
                "password": "password",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Login successful")

    def test_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            {"email": "invalid@django.com", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid email or password")

    def test_logout_view(self):
        user = User.objects.create_user(email="logout@django.com", password="password")
        self.client.force_login(user)
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Logout successful")

    def test_protected_view_authenticated(self):
        user = User.objects.create_user(
            email="protected@django.com", password="password", role="gold"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("protected"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello, protected@django.com", response.json()["message"])

    def test_protected_view_unauthenticated(self):
        response = self.client.get(reverse("protected"))
        self.assertEqual(response.status_code, 302)
