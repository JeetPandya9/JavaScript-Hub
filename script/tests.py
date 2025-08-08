from django.test import TestCase
from django.test import Client
from django.urls import reverse
from .models import User, Contact

# Create your tests here.
class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            firstname="John",
            lastname="Doe",
            email="john@example.com"
        )
        self.user.set_password("testpassword123")
        self.user.save()

    def test_user_creation(self):
        self.assertEqual(self.user.firstname, "John")
        self.assertEqual(self.user.lastname, "Doe")
        self.assertEqual(self.user.email, "john@example.com")
        self.assertTrue(self.user.check_password("testpassword123"))

    def test_user_str_representation(self):
        self.assertEqual(str(self.user), "John Doe")

class ContactModelTest(TestCase):
    def setUp(self):
        self.contact = Contact.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            subject="Test Message",
            message="This is a test message."
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.name, "Jane Smith")
        self.assertEqual(self.contact.email, "jane@example.com")
        self.assertEqual(self.contact.subject, "Test Message")
        self.assertEqual(self.contact.message, "This is a test message.")

    def test_contact_str_representation(self):
        self.assertEqual(str(self.contact), "Jane Smith - Test Message")

class RegistrationViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_page_loads(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')

    def test_user_registration(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = self.client.post(reverse('registration'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            firstname="Test",
            lastname="User",
            email="test@example.com"
        )
        self.user.set_password("testpass123")
        self.user.save()

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_user_login(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_page_loads(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')

    def test_contact_form_submission(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        response = self.client.post(reverse('contact'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission
        self.assertTrue(Contact.objects.filter(email='test@example.com').exists())
