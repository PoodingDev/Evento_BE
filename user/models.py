import random
import string

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def generate_random_nickname(self):
        return "".join(random.choices(string.ascii_letters + string.digits, k=8))

    def create_user(self, email, username, birth, password=None, nickname=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        if not birth:
            raise ValueError("Users must have a birth date")

        nickname = nickname or self.generate_random_nickname()

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            birth=birth,
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, birth, password):
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            birth=birth,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30)
    birth = models.DateField()
    nickname = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "birth"]

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user_user"
