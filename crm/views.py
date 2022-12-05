import jwt
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, authentication
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from crm.models import Course, User, Enrollment, Lesson, Message
from crm.serializers import (UserSerializer, CourseShortSerializer, RegistrationSerializer, LoginSerializer,
                             CourseSerializer, FullCourseSerializer, StudentFullCourseSerializer, LessonSerializer,
                             UserUpdateSerializer, SentMessageSerializer, ContactMessageSerializer,
                             ReceivedMessageSerializer, AllCourseUsers)
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
            queryset = user.courses.all()

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
    #     user, token = get_token(;request)
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
        user, token = get_token(request)
        data = request.data.get('data', {})

        if Course.objects.get(id=data['course_id']).author == user:
            new_data = {
                'email': user.email,
                'password': None,
                'token': token,
                'name': user.name
            }

            serializer = UserSerializer(user, data=new_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            course_serializer = self.serializer_class(Course.objects.get(id=data['course_id']), data=data, partial=True)
            course_serializer.is_valid(raise_exception=True)
            course_serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        user, token = get_token(request)
        print(pk)
        if request.method == 'DELETE' and Course.objects.get(pk=pk).author == user:
            new_data = {
                'email': user.email,
                'password': None,
                'token': token,
                'name': user.name
            }

            serializer = UserSerializer(user, data=new_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            Course.objects.get(pk=pk).delete()
            return Response(serializer.data, status.HTTP_200_OK)

        return Response({}, status.HTTP_404_NOT_FOUND)

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
            # 'password': user.password,
            'token': token,
            'name': user.name
        }

        course = Course.objects.get(id=data['course_id'], author=user)
        lesson, _ = Lesson.objects.get_or_create(
            course=course,
            number=data['number'],
            name=data['name'],
            description=data['description']
        )

        lesson.save()

        serializer = UserSerializer(user, data=new_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # else:
    #     return Response({}, status=status.HTTP_404_NOT_FOUND)


class MessageApiView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,)
    # serializer_class = MessageSerializer

    def get(self, request):
        user, token = get_token(request)

        user_messages = Message.objects.filter(Q(sent_from=user)|Q(sent_to=user)).order_by('sent_at')
        print(user_messages)
        # msg_from_user = Message.objects.filter(sent_from=user).order_by('sent_at')
        msg_dict = {}
        for message in user_messages:
            if message.sent_from == user:
                if message.sent_to.id in msg_dict:
                    msg_dict[message.sent_to.id].append(SentMessageSerializer(message).data)
                else:
                    msg_dict[message.sent_to.id] = [SentMessageSerializer(message).data]
            elif message.sent_to == user:
                if message.sent_from.id in msg_dict:
                    msg_dict[message.sent_from.id].append(ReceivedMessageSerializer(message).data)
                else:
                    msg_dict[message.sent_from.id] = [ReceivedMessageSerializer(message).data]

        print(msg_dict)

        return Response(msg_dict, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        user, token = get_token(request)

        data = request.data.get('data', {})
        print(data)

        sent_to = User.objects.get(id=data['send_to'])
        print(sent_to)

        new_data = {
            'text': data['text'],
            'sent_from': user,
            'sent_to': sent_to
            }

        serializer = ContactMessageSerializer(new_data)

        message = Message.objects.create(text=data['text'], sent_from=user, sent_to=sent_to)
        message.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AllCourseUsersApiView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)

    def get(self, request):
        user, token = get_token(request)

        courses = user.courses.all()
        print(courses)

        course_dict = {'teachers': [], 'students': []}
        all_course_users = []
        for course in courses:
            course_users = User.objects.filter(courses=course)
            all_course_users.extend(iter(course_users))
        print(all_course_users)

        all_course_users = set(all_course_users[:])
        print(all_course_users)

        for temp_user in all_course_users:
            if temp_user != user and user.role.id == 3 and temp_user.role.id == 2:
                course_dict['teachers'].append(AllCourseUsers(temp_user).data)

            elif temp_user != user and temp_user.role.id == 3:
                course_dict['students'].append(AllCourseUsers(temp_user).data)

            else:
                print(temp_user.role)

        print(course_dict)

        return Response(course_dict, status=status.HTTP_200_OK)
