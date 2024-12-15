from django.urls import path
from api.activity.activity_views import *

urlpatterns = [
    path('list/', ActivityLogListView.as_view(), name='activity_log_list'),
    path('detail/<int:pk>/', ActivityLogDetailView.as_view(), name='activity_log_detail'),
    path('create/', ActivityLogCreateView.as_view(), name='activity_log_create'),
]
