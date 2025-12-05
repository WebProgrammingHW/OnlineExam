# attempts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from .models import Attempt, Answer
from .forms import ShortAnswerForm, MCQAnswerForm, FileAnswerForm
from questions.models import Exam, Question


def student_required(view_func):
    """Decorator to check if user is a student"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_student():
            messages.error(request, 'فقط دانشجویان به این بخش دسترسی دارند.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator([login_required, student_required], name='dispatch')
class ExamListView(View):
    template_name = 'attempts/exam_list.html'

    def get(self, request):
        now = timezone.now()
        taken_exam_ids = Attempt.objects.filter(student=request.user).values_list('exam_id', flat=True)
        
        available_exams = Exam.objects.filter(
            published=True,
            start_at__lte=now
        ).exclude(id__in=taken_exam_ids)
        
        return render(request, self.template_name, {'exams': available_exams})


@method_decorator([login_required, student_required], name='dispatch')
class StartExamView(View):
    template_name = 'attempts/start_exam.html'

    def get(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, published=True)
        
        # Check if already attempted
        existing_attempt = Attempt.objects.filter(student=request.user, exam=exam).first()
        if existing_attempt:
            if existing_attempt.status == 'in_progress':
                return redirect('attempts:take_exam', attempt_pk=existing_attempt.pk)
            else:
                messages.warning(request, 'شما قبلاً در این آزمون شرکت کرده‌اید.')
                return redirect('attempts:my_attempts')
        
        return render(request, self.template_name, {'exam': exam})

    def post(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, published=True)
        
        # Check if already attempted
        existing_attempt = Attempt.objects.filter(student=request.user, exam=exam).first()
        if existing_attempt:
            messages.warning(request, 'شما قبلاً در این آزمون شرکت کرده‌اید.')
            return redirect('attempts:my_attempts')
        
        # Create new attempt
        attempt = Attempt.objects.create(
            student=request.user,
            exam=exam,
            status='in_progress'
        )
        
        # Create empty answers for all questions
        for question in exam.questions.all():
            Answer.objects.create(
                attempt=attempt,
                question=question
            )
        
        messages.success(request, 'آزمون شروع شد. موفق باشید!')
        return redirect('attempts:take_exam', attempt_pk=attempt.pk)


@method_decorator([login_required, student_required], name='dispatch')
class TakeExamView(View):
    template_name = 'attempts/take_exam.html'

    def get(self, request, attempt_pk):
        attempt = get_object_or_404(Attempt, pk=attempt_pk, student=request.user)
        
        if attempt.status != 'in_progress':
            messages.warning(request, 'این آزمون قبلاً ارسال شده است.')
            return redirect('attempts:attempt_result', attempt_pk=attempt.pk)
        
        # Calculate remaining time
        end_time = attempt.start_time + timedelta(minutes=attempt.exam.duration_minutes)
        now = timezone.now()
        
        if now >= end_time:
            # Auto submit if time is up
            attempt.submit()
            messages.warning(request, 'زمان آزمون به پایان رسید و پاسخ‌های شما ثبت شد.')
            return redirect('attempts:attempt_result', attempt_pk=attempt.pk)
        
        remaining_seconds = int((end_time - now).total_seconds())
        
        questions = attempt.exam.questions.all()
        answers = {a.question_id: a for a in attempt.answers.all()}
        
        # Build question list with answers
        question_list = []
        for q in questions:
            answer = answers.get(q.id)
            question_list.append({
                'question': q,
                'answer': answer,
                'choices': q.choices.all() if q.qtype == Question.TYPE_MCQ else None
            })
        
        return render(request, self.template_name, {
            'attempt': attempt,
            'question_list': question_list,
            'remaining_seconds': remaining_seconds,
            'end_time': end_time.isoformat()
        })

    def post(self, request, attempt_pk):
        attempt = get_object_or_404(Attempt, pk=attempt_pk, student=request.user)
        
        if attempt.status != 'in_progress':
            messages.warning(request, 'این آزمون قبلاً ارسال شده است.')
            return redirect('attempts:attempt_result', attempt_pk=attempt.pk)
        
        # Save answers
        for question in attempt.exam.questions.all():
            answer = attempt.answers.filter(question=question).first()
            if not answer:
                answer = Answer.objects.create(attempt=attempt, question=question)
            
            if question.qtype == Question.TYPE_SHORT:
                answer.text_answer = request.POST.get(f'question_{question.id}', '')
            elif question.qtype == Question.TYPE_MCQ:
                choice_id = request.POST.get(f'question_{question.id}')
                if choice_id:
                    answer.selected_choice_id = int(choice_id)
            elif question.qtype == Question.TYPE_FILE:
                file = request.FILES.get(f'question_{question.id}')
                if file:
                    answer.uploaded_file = file
            
            answer.save()
        
        # Check if submitting or just saving
        if 'submit' in request.POST:
            attempt.submit()
            messages.success(request, 'آزمون با موفقیت ارسال شد.')
            return redirect('attempts:attempt_result', attempt_pk=attempt.pk)
        
        messages.success(request, 'پاسخ‌ها ذخیره شد.')
        return redirect('attempts:take_exam', attempt_pk=attempt.pk)


@method_decorator([login_required, student_required], name='dispatch')
class MyAttemptsView(View):
    template_name = 'attempts/my_attempts.html'

    def get(self, request):
        attempts = Attempt.objects.filter(student=request.user).select_related('exam')
        return render(request, self.template_name, {'attempts': attempts})


@method_decorator([login_required, student_required], name='dispatch')
class AttemptResultView(View):
    template_name = 'attempts/attempt_result.html'

    def get(self, request, attempt_pk):
        attempt = get_object_or_404(Attempt, pk=attempt_pk, student=request.user)
        answers = attempt.answers.select_related('question', 'selected_choice').all()
        
        return render(request, self.template_name, {
            'attempt': attempt,
            'answers': answers
        })


@login_required
def get_remaining_time(request, attempt_pk):
    """AJAX endpoint to get remaining time"""
    attempt = get_object_or_404(Attempt, pk=attempt_pk, student=request.user)
    
    if attempt.status != 'in_progress':
        return JsonResponse({'remaining': 0, 'expired': True})
    
    end_time = attempt.start_time + timedelta(minutes=attempt.exam.duration_minutes)
    now = timezone.now()
    remaining = max(0, int((end_time - now).total_seconds()))
    
    return JsonResponse({
        'remaining': remaining,
        'expired': remaining <= 0
    })