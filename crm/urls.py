from django.urls import path

from .views import (RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView, AllCourseAPIView,
                    CourseRetrieveUpdateAPIView, UserCourseAPIView, CourseApiView, LessonRetrieveUpdateAPIView,
                    MessageApiView, AllCourseUsersApiView)

app_name = 'crm'
urlpatterns = [
    path('sign_up/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('courses/', AllCourseAPIView.as_view()),
    path('courses/<int:pk>', CourseApiView.as_view()),
    # path('courses/<int:pk>/add_course/', UserCourseAPIView.as_view()),
    path('add_course/', UserCourseAPIView.as_view()),
    path('courses/<int:pk>/add_lesson/', LessonRetrieveUpdateAPIView.as_view()),
    path('courses/<int:pk>/edit/', CourseRetrieveUpdateAPIView.as_view()),
    path('courses/<int:pk>/delete/', CourseRetrieveUpdateAPIView.as_view()),
    path('courses/my_courses/', UserCourseAPIView.as_view()),
    path('courses/my_courses/<int:pk>', CourseApiView.as_view()),
    path('messages/', MessageApiView.as_view()),
    path('all_course_users/', AllCourseUsersApiView.as_view()),
]
