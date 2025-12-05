# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Count, Avg

from questions.models import Exam
from attempts.models import Attempt


@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        user = request.user
        context = {}

        if user.is_teacher():
            # Teacher dashboard
            exams = Exam.objects.filter(teacher=user)
            context['exams'] = exams
            context['total_exams'] = exams.count()
            context['published_exams'] = exams.filter(published=True).count()
            context['total_attempts'] = Attempt.objects.filter(exam__teacher=user).count()
            context['pending_grading'] = Attempt.objects.filter(
                exam__teacher=user,
                status='submitted'
            ).count()
            return render(request, 'dashboard/teacher_home.html', context)

        else:
            # Student dashboard
            now = timezone.now()
            
            # Available exams (published and not yet taken)
            taken_exam_ids = Attempt.objects.filter(student=user).values_list('exam_id', flat=True)
            available_exams = Exam.objects.filter(
                published=True,
                start_at__lte=now
            ).exclude(id__in=taken_exam_ids)
            
            # My attempts
            my_attempts = Attempt.objects.filter(student=user).select_related('exam')
            
            context['available_exams'] = available_exams
            context['my_attempts'] = my_attempts
            context['completed_count'] = my_attempts.filter(status='graded').count()
            context['in_progress_count'] = my_attempts.filter(status='in_progress').count()
            
            return render(request, 'dashboard/student_home.html', context)


@method_decorator(login_required, name='dispatch')
class SearchExamsView(View):
    template_name = 'dashboard/search_exams.html'

    def get(self, request):
        query = request.GET.get('q', '')
        topic = request.GET.get('topic', '')
        
        exams = Exam.objects.filter(published=True)
        
        if query:
            exams = exams.filter(title__icontains=query)
        if topic:
            exams = exams.filter(topic__icontains=topic)
        
        # Get unique topics for filter
        topics = Exam.objects.filter(published=True).values_list('topic', flat=True).distinct()
        
        context = {
            'exams': exams,
            'query': query,
            'topic': topic,
            'topics': topics,
        }
        return render(request, self.template_name, context)