# attempts/urls.py
from django.urls import path
from . import views

app_name = 'attempts'

urlpatterns = [
    path('exams/', views.ExamListView.as_view(), name='exam_list'),
    path('exams/<int:exam_pk>/start/', views.StartExamView.as_view(), name='start_exam'),
    path('<int:attempt_pk>/take/', views.TakeExamView.as_view(), name='take_exam'),
    path('<int:attempt_pk>/result/', views.AttemptResultView.as_view(), name='attempt_result'),
    path('my/', views.MyAttemptsView.as_view(), name='my_attempts'),
    path('<int:attempt_pk>/time/', views.get_remaining_time, name='remaining_time'),
]