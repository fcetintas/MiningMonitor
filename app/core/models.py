from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
    PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **kwargs):
        """
        Creates and saves a new user
        """
        if not email:
            raise ValueError("User must have email address")
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves new superuser
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Device(models.Model):
    """Mining device object"""
    ip = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    port = models.IntegerField()
    expected_gpu = models.IntegerField()
    expected_gpu_speed = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name + "-" + self.ip + ":" + str(self.port)
