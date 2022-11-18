from django.contrib import admin
from .models import User, Course, UserRole

admin.site.register(User)
admin.site.register(Course)
admin.site.register(UserRole)
# Register your models here.
