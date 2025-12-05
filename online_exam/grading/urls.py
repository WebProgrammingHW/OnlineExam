# grading/urls.py
from django.urls import path
from . import views

app_name = 'grading'

urlpatterns = [
    path('', views.AttemptListView.as_view(), name='attempt_list'),
    path('<int:attempt_pk>/', views.GradeAttemptView.as_view(), name='grade_attempt'),
    path('<int:attempt_pk>/auto/', views.AutoGradeAttemptView.as_view(), name='auto_grade'),
]