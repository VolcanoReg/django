from django.urls import path
from . import views

urlpatterns = [
    path('test-crud/', views.testing_crud, name='test_crud'),
    path('allcourse/', views.allcourse, name='allcourse'),
    path('course-stat/', views.courseStat, name='course_stat'),
    path('member-stat/', views.courseMemberStat, name='member_stat'),
    path('user-stats/', views.userStats, name='user_stats'),
]