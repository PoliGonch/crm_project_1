import jwt
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.core.cache import cache
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import MinLengthValidator
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
import bcrypt

clients_dict = {}
salt_dict = {}


class UserManager(BaseUserManager):

    def create_user(self, email, password, name, surname, role):

        if name is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        if role is None:
            raise TypeError('Users must have a role.')

        # role_done, _ = UserRole.objects.get_or_create(name=role)
        user = self.model(email=self.normalize_email(email), name=name, surname=surname, role=role)
        # user.set_password(self.get_hash(password))
        user.set_password(password)
        user.save()

        return user

    # @staticmethod
    # def get_hash(password):
    #     byte_pwd = password.encode('utf-8')
    #
    #     print(salt_dict)
    #     if password in salt_dict.keys():
    #         my_salt = salt_dict[password]
    #         print('qwa')
    #     else:
    #         my_salt = bcrypt.gensalt()
    #         salt_dict[password] = my_salt
    #     return bcrypt.hashpw(byte_pwd, my_salt)

    def create_superuser(self, name, email, password):
        if password is None:
            raise TypeError('Superusers must have a password.')

        role, _ = UserRole.objects.get_or_create(name='Superuser')
        user = self.create_user(name=name, surname=None, email=email, role=role, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(db_index=True, unique=True)
    password = models.CharField(max_length=200, unique=False)
    name = models.CharField(max_length=200, unique=False)
    surname = models.CharField(max_length=200, unique=False, blank=True, null=True)
    role = models.ForeignKey('UserRole', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    courses = models.ManyToManyField('Course', through='Enrollment')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.name + self.surname

    def get_short_name(self):
        return self.name

    # def _generate_jwt_token(self):
    #     refresh = RefreshToken.for_user(self)
    #
    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }

    def _generate_jwt_token(self):

        dt = datetime.now() + timedelta(days=7)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        # print(token)
        # payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        # print(payload)

        return token



    # @property
    # def get_hash(self):
    #     ...
    #
    # @property
    # def get_token(self):
    #     ...
    # def set_password(self, password):
    #     self.password = password


class UserRole(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=500, unique=True)
    image = models.ImageField(blank=True, null=True)
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def create(self, name, description):
        course = Course(name=name, description=description)
        course.save()
        return course


class Lesson(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField()


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(default=timezone.now)  # дата поступления
    completed = models.BooleanField(null=True, blank=True)
