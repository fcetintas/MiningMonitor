from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTest(TestCase):

    def test_create_user(self):
        """Test if creating user with email is successful"""
        email = 'test@test.com'
        password = 'password1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_create_super_user(self):
        """Test if superuser is successfully created"""
        email = 'test@test.com'
        password = 'password'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_device_str(self):
        """Test device string representation"""
        device = models.Device.objects.create(
            ip="192.168.1.111",
            name="name",
            port=3300,
            expected_gpu=12,
            expected_gpu_speed=31.3
        )
        output = (device.name + "-" + device.ip + ":" + str(device.port))
        self.assertEqual(str(device), output)
