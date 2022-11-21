from django.contrib.auth import authenticate
from rest_framework import serializers

from crm.models import User, Course, Lesson


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
            # error_data = {
            #     'error': 'An email address is required to log in!'
            # }
            # return error_data

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
            'role': user.role.id,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        return obj.role.id

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'role', 'token',)

        read_only_fields = ('token',)


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        return obj.role.id

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'role', 'password', 'token',)

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
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        if obj.author:
            return obj.author.name + " " + obj.author.surname
        return None

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'author', 'price']


class CourseSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        if obj.author:
            return obj.author.name + " " + obj.author.surname
        else:
            return None

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'author']

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
    author = serializers.SerializerMethodField()
    lesson = LessonSerializer()

    def get_author(self, obj):
        if obj.author:
            return obj.author.name + " " + obj.author.surname
        else:
            return None

    def get_users(self, obj):
        users = User.objects.filter(courses=obj)
        serializer = TeacherViewUserSerializer(data=users, many=True)
        serializer.is_valid()
        return serializer.data

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'lesson', 'users', 'author']
        # read_only_fields = '__all__'


class StudentFullCourseSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer()

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'image', 'lesson']
