# questions/urls.py
from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    # Exam URLs
    path('', views.ExamListView.as_view(), name='exam_list'),
    path('create/', views.ExamCreateView.as_view(), name='exam_create'),
    path('<int:pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
    path('<int:pk>/edit/', views.ExamUpdateView.as_view(), name='exam_update'),
    path('<int:pk>/delete/', views.ExamDeleteView.as_view(), name='exam_delete'),
    
    # Question URLs
    path('<int:exam_pk>/questions/add/', views.QuestionCreateView.as_view(), name='question_create'),
    path('questions/<int:pk>/edit/', views.QuestionUpdateView.as_view(), name='question_update'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question_delete'),
]