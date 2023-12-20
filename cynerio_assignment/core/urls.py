from django.urls import re_path

from cynerio_assignment.core.views import TaskView, CynerioTaskReportView

app_name = 'core'

urlpatterns = [
    re_path(r'^api/v1/task/$', TaskView.as_view(), name='task'),
    re_path(r'^api/v1/task_report/$', CynerioTaskReportView.as_view(), name='task_report'),

]
