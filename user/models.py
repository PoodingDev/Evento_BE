from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, user_id, email, username, birth, nickname, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            user_id=user_id,
            email=self.normalize_email(email),
            username=username,
            birth=birth,
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, email, username, birth, nickname, password):
        user = self.create_user(
            user_id=user_id,
            email=email,
            password=password,
            username=username,
            birth=birth,
            nickname=nickname,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30)
    birth = models.DateField()
    nickname = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['email', 'username', 'birth', 'nickname']

    def __str__(self):
        return self.user_id