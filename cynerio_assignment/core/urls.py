from django.contrib import admin
from django.urls import path, re_path

from cynerio_assignment.core.views import TaskView

urlpatterns = [
    re_path('api/v1/task/', TaskView.as_view(), name='task'),
]
