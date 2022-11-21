import jwt
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, authentication
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from crm.models import Course, User, Enrollment, Lesson
from crm.serializers import (UserSerializer, CourseShortSerializer, RegistrationSerializer, LoginSerializer,
                             CourseSerializer, FullCourseSerializer, StudentFullCourseSerializer, LessonSerializer,
                             UserUpdateSerializer)
from crm_project import settings
from .renderers import UserJSONRenderer


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     # queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
# permission_classes = [permissions.IsAuthenticated]

class CourseAPIViewSet(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseShortSerializer


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})
        # print(user)

        serializer = self.serializer_class(data=user)
        # print('1')
        serializer.is_valid(raise_exception=True)
        # print(serializer.validated_data)
        serializer.save()
        print(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        print(serializer.validated_data)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCourseAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CourseShortSerializer

    def get(self, request, *args, **kwargs):
        user, token = get_token(request)
        if user.role.id not in [2, 3]:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        if user.role.id == 2:
            queryset = Course.objects.filter(author=user)
            serializer = FullCourseSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if user.role.id == 3:
            queryset = request.user.courses.all()

            serializer = self.serializer_class(queryset, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user, token = get_token(request)

        if user.role.id not in [2, 3]:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('data', {})
        # print(f'{data=}')

        new_data = {
            'email': user.email,
            'password': None,
            'token': token,
            'name': user.name
        }

        if user.role.id == 3:
            user_course, _ = Enrollment.objects.get_or_create(
                student=user,
                course=get_object_or_404(Course, pk=data['course_id']),
            )
            user_course.save()

            # return Response(serializer.data, status=status.HTTP_201_CREATED)

        if user.role.id == 2:
            course = Course.objects.create(**data, author=user)
            course.save()

        serializer = UserSerializer(user, data=new_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response({}, status=status.HTTP_404_NOT_FOUND)


class AllCourseAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CourseShortSerializer

    def get(self, request):
        queryset = Course.objects.all()
        print(queryset)
        serializer = self.serializer_class(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


def get_token(request):
    auth_header = authentication.get_authorization_header(request).split()
    token = auth_header[0].decode('utf-8')
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    user = User.objects.get(pk=payload['id'])

    return user, token


class CourseRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = CourseSerializer

    # def post(self, request):
    #     user, token = get_token(request)
    #
    #     if user.role.id != 2:
    #         return Response({}, status=status.HTTP_404_NOT_FOUND)
    #
    #     data = request.data.get('data', {})
    #     print(f'{data=}')
    #
    #     new_data = {
    #         'email': user.email,
    #         'password': user.password,
    #         'token': token,
    #         'name': user.name
    #     }
    #
    #     course = Course.objects.create(**data)
    #     course.save()
    #
    #     serializer = UserSerializer(user, data=new_data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('data', {})

        serializer = self.serializer_class(
            request.data, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def __delete__(self, request):
        user, token = get_token(request)
        if request.method == 'DELETE' and user.is_superuser and request.data.course_id:
            Course.objects.filter(pk=request.data.course_id).delete()


class CourseApiView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    serializer_class = StudentFullCourseSerializer

    def get(self, request, pk=None):
        user, token = get_token(request)

        if user.role.id not in [2, 3]:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        if user.role.id == 2:
            queryset = Course.objects.get(id=pk, author=user)
            # print(queryset)
            serializer = FullCourseSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if user.role.id == 3:
            queryset = Course.objects.get(id=pk)
            serializer = self.serializer_class(queryset)

            return Response(serializer.data, status=status.HTTP_200_OK)


class LessonRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LessonSerializer

    def post(self, request, *args, **kwargs):
        user, token = get_token(request)

        if user.role.id != 2:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.get('data', {})
        print(data)

        new_data = {
            'email': user.email,
            'password': user.password,
            'token': token,
            'name': user.name
        }

        course = Course.objects.get(id=data['course_id'], author=user)
        lesson, _ = Lesson.objects.get_or_create(
            number=data['number'],
            name=data['name'],
            description=data['description']
        )
        course.lesson = lesson
        course.save()

        serializer = UserSerializer(user, data=new_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # else:
    #     return Response({}, status=status.HTTP_404_NOT_FOUND)
