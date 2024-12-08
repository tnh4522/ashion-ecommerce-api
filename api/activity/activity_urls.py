from django.urls import path
from api.activity.activity_views import *

urlpatterns = [
    path('list/', ActivityLogListView.as_view(), name='activity_log_list'),
    path('create/', ActivityLogCreateView.as_view(), name='activity_log_create'),
]
