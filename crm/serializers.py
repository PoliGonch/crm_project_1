from rest_framework import serializers

from crm.backends import JWTAuthentication
from crm.models import User, Course, UserRole, UserManager, Enrollment, Lesson
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.core import serializers as srzr


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['token', 'email', 'password', 'name', 'surname', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    # class Meta:
    #     model = User
    #     fields = ['token', 'email', 'password', 'name', 'surname', 'role']

    def validate(self, data):
        email = data.get('email', None)
        # password = UserManager.get_hash(data.get('password'))
        password = data.get('password', None)

        print(email, password)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)
        print(user)

        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'email': user.email,
            'name': user.name,
            'surname': user.surname,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'token',)

        read_only_fields = ('token',)


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'password', 'token',)

        read_only_fields = ('token',)

    def update(self, instance, validated_data):

        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class CourseShortSerializer(serializers.ModelSerializer):
    # description = serializers.CharField(max_length=500, unique=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image']

        read_only_fields = '__all__'

    def create(self, validated_data):
        return Course.objects.create(**validated_data)


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = ['id', 'number', 'name', 'description']


class TeacherViewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname']

        read_only_fields = ('id', 'name', 'surname')


class FullCourseSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    lesson = LessonSerializer()

    def get_users(self, obj):
        users = User.objects.filter(courses=obj)
        serializer = TeacherViewUserSerializer(data=users, many=True)
        serializer.is_valid()
        return serializer.data

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'lesson', 'users']
        # read_only_fields = '__all__'


class StudentFullCourseSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'lesson']