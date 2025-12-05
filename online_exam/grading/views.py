# grading/views.py
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.utils import timezone

from .models import ManualReview, AutoGraderLog
from .forms import GradeAnswerForm
from attempts.models import Attempt, Answer
from questions.models import Question
from notifications.models import Notification


def teacher_required(view_func):
    """Decorator to check if user is a teacher"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_teacher():
            messages.error(request, 'فقط اساتید به این بخش دسترسی دارند.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def auto_grade_answer(answer):
    """Automatically grade short answer and MCQ questions"""
    question = answer.question
    
    if question.qtype == Question.TYPE_MCQ:
        # MCQ auto grading
        if answer.selected_choice and answer.selected_choice.is_correct:
            answer.score = question.max_score
            matched = True
        else:
            answer.score = 0
            matched = False
        
        answer.is_auto_graded = True
        answer.graded_at = timezone.now()
        answer.save()
        
        AutoGraderLog.objects.create(
            answer=answer,
            matched=matched,
            awarded_score=answer.score,
            reason='چندگزینه‌ای - تصحیح خودکار'
        )
        return True
    
    elif question.qtype == Question.TYPE_SHORT and question.auto_grade_regex:
        # Short answer auto grading with regex
        pattern = question.auto_grade_regex.strip()
        text = (answer.text_answer or '').strip()
        
        try:
            if re.fullmatch(pattern, text, re.IGNORECASE):
                answer.score = question.max_score
                matched = True
            else:
                answer.score = 0
                matched = False
            
            answer.is_auto_graded = True
            answer.graded_at = timezone.now()
            answer.save()
            
            AutoGraderLog.objects.create(
                answer=answer,
                matched=matched,
                awarded_score=answer.score,
                reason=f'تطبیق با الگو: {pattern}'
            )
            return True
        except re.error:
            # Invalid regex, needs manual grading
            answer.needs_manual = True
            answer.save()
            return False
    
    elif question.qtype == Question.TYPE_FILE:
        # File answers always need manual grading
        answer.needs_manual = True
        answer.save()
        return False
    
    else:
        # No auto grade regex, needs manual
        answer.needs_manual = True
        answer.save()
        return False


@method_decorator([login_required, teacher_required], name='dispatch')
class AttemptListView(View):
    template_name = 'grading/attempt_list.html'

    def get(self, request):
        attempts = Attempt.objects.filter(
            exam__teacher=request.user,
            status__in=['submitted', 'graded']
        ).select_related('exam', 'student')
        
        return render(request, self.template_name, {'attempts': attempts})


@method_decorator([login_required, teacher_required], name='dispatch')
class GradeAttemptView(View):
    template_name = 'grading/grade_attempt.html'

    def get(self, request, attempt_pk):
        attempt = get_object_or_404(Attempt, pk=attempt_pk, exam__teacher=request.user)
        answers = attempt.answers.select_related('question', 'selected_choice').all()
        
        # Build forms for each answer
        answer_forms = []
        for answer in answers:
            form = GradeAnswerForm(
                max_score=answer.question.max_score,
                initial={'score': answer.score, 'comments': ''},
                prefix=f'answer_{answer.id}'
            )
            answer_forms.append({
                'answer': answer,
                'form': form
            })
        
        return render(request, self.template_name, {
            'attempt': attempt,
            'answer_forms': answer_forms
        })

    def post(self, request, attempt_pk):
        attempt = get_object_or_404(Attempt, pk=attempt_pk, exam__teacher=request.user)
        answers = attempt.answers.all()
        
        total_score = 0
        all_graded = True
        
        for answer in answers:
            form = GradeAnswerForm(
                request.POST,
                max_score=answer.question.max_score,
                prefix=f'answer_{answer.id}'
            )
            
            if form.is_valid():
                score = form.cleaned_data['score']
                comments = form.cleaned_data.get('comments', '')
                
                answer.score = score
                answer.graded_by = request.user
                answer.graded_at = timezone.now()
                answer.is_auto_graded = False
                answer.needs_manual = False
                answer.save()
                
                # Create or update manual review
                review, created = ManualReview.objects.get_or_create(answer=answer)
                review.reviewer = request.user
                review.final_score = score
                review.comments = comments
                review.reviewed_at = timezone.now()
                review.save()
                
                total_score += score
            else:
                all_graded = False
        
        if all_graded:
            attempt.total_score = total_score
            attempt.status = 'graded'
            attempt.save()
            
            # Send notification to student
            Notification.objects.create(
                user=attempt.student,
                notif_type='score',
                channel='in_app',
                title=f'نمره آزمون {attempt.exam.title}',
                message=f'نمره شما در آزمون {attempt.exam.title}: {total_score} از {attempt.exam.total_score}'
            )
            
            messages.success(request, 'نمره‌گذاری با موفقیت انجام شد.')
        else:
            messages.warning(request, 'برخی پاسخ‌ها نمره‌گذاری نشد.')
        
        return redirect('grading:attempt_list')


@method_decorator([login_required, teacher_required], name='dispatch')
class AutoGradeAttemptView(View):
    """Auto grade MCQ and short answer questions"""

    def post(self, request, attempt_pk):
        attempt = get_object_or_404(Attempt, pk=attempt_pk, exam__teacher=request.user)
        
        auto_graded_count = 0
        manual_needed_count = 0
        
        for answer in attempt.answers.all():
            if answer.score is None:  # Not already graded
                if auto_grade_answer(answer):
                    auto_graded_count += 1
                else:
                    manual_needed_count += 1
        
        # Calculate total score if all graded
        answers = attempt.answers.all()
        if all(a.score is not None for a in answers):
            attempt.total_score = sum(a.score for a in answers)
            attempt.status = 'graded'
            attempt.save()
        
        messages.success(request, 
            f'{auto_graded_count} پاسخ به صورت خودکار تصحیح شد. '
            f'{manual_needed_count} پاسخ نیاز به تصحیح دستی دارد.'
        )
        
        return redirect('grading:grade_attempt', attempt_pk=attempt_pk)