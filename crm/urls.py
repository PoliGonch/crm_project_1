from django.urls import path

from .views import (RegistrationAPIView, LoginAPIView, UserRetrieveUpdateAPIView, AllCourseAPIView,
                    CourseRetrieveUpdateAPIView, UserCourseAPIView, CourseApiView, LessonRetrieveUpdateAPIView)

app_name = 'crm'
urlpatterns = [
    path('sign_up/', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('user/', UserRetrieveUpdateAPIView.as_view()),
    path('courses/', AllCourseAPIView.as_view()),
    path('courses/<int:pk>', CourseApiView.as_view()),
    path('courses/<int:pk>/add_course/', UserCourseAPIView.as_view()), #allows user to add himself to the course
    path('add_course/', UserCourseAPIView.as_view()),
    path('courses/<int:pk>/add_lesson/', LessonRetrieveUpdateAPIView.as_view()),
    path('courses/<int:pk>/edit/', CourseRetrieveUpdateAPIView.as_view()),
    path('courses/my_courses/', UserCourseAPIView.as_view()),
    path('courses/my_courses/<int:pk>', CourseApiView.as_view()),
]
