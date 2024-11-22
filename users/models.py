from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, user_login_id, user_email, user_name, user_birth, user_nickname, password=None):
        if not user_email:
            raise ValueError('Users must have an email address')
        user = self.model(
            user_login_id=user_login_id,
            user_email=self.normalize_email(user_email),
            user_name=user_name,
            user_birth=user_birth,
            user_nickname=user_nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_login_id, user_email, user_name, user_birth, user_nickname, password):
        user = self.create_user(
            user_login_id=user_login_id,
            user_email=user_email,
            password=password,
            user_name=user_name,
            user_birth=user_birth,
            user_nickname=user_nickname,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    user_login_id = models.CharField(max_length=30, unique=True)
    user_email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=30)
    user_birth = models.DateField()
    user_nickname = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'user_login_id'
    REQUIRED_FIELDS = ['user_email', 'user_name', 'user_birth', 'user_nickname']

    def __str__(self):
        return self.user_login_id
