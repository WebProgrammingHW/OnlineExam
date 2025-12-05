# questions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.http import HttpResponseForbidden

from .models import Exam, Question, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm, ChoiceFormSet


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


@method_decorator([login_required, teacher_required], name='dispatch')
class ExamListView(View):
    template_name = 'questions/exam_list.html'

    def get(self, request):
        exams = Exam.objects.filter(teacher=request.user)
        return render(request, self.template_name, {'exams': exams})


@method_decorator([login_required, teacher_required], name='dispatch')
class ExamCreateView(View):
    template_name = 'questions/exam_form.html'

    def get(self, request):
        form = ExamForm()
        return render(request, self.template_name, {'form': form, 'title': 'ایجاد آزمون جدید'})

    def post(self, request):
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.teacher = request.user
            exam.save()
            messages.success(request, 'آزمون با موفقیت ایجاد شد.')
            return redirect('questions:exam_detail', pk=exam.pk)
        return render(request, self.template_name, {'form': form, 'title': 'ایجاد آزمون جدید'})


@method_decorator([login_required, teacher_required], name='dispatch')
class ExamDetailView(View):
    template_name = 'questions/exam_detail.html'

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, teacher=request.user)
        questions = exam.questions.all()
        return render(request, self.template_name, {
            'exam': exam,
            'questions': questions
        })


@method_decorator([login_required, teacher_required], name='dispatch')
class ExamUpdateView(View):
    template_name = 'questions/exam_form.html'

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, teacher=request.user)
        form = ExamForm(instance=exam)
        return render(request, self.template_name, {
            'form': form,
            'exam': exam,
            'title': 'ویرایش آزمون'
        })

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, teacher=request.user)
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'آزمون با موفقیت به‌روزرسانی شد.')
            return redirect('questions:exam_detail', pk=exam.pk)
        return render(request, self.template_name, {
            'form': form,
            'exam': exam,
            'title': 'ویرایش آزمون'
        })


@method_decorator([login_required, teacher_required], name='dispatch')
class ExamDeleteView(View):
    template_name = 'questions/exam_confirm_delete.html'

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, teacher=request.user)
        return render(request, self.template_name, {'exam': exam})

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, teacher=request.user)
        exam.delete()
        messages.success(request, 'آزمون با موفقیت حذف شد.')
        return redirect('questions:exam_list')


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionCreateView(View):
    template_name = 'questions/question_form.html'

    def get(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, teacher=request.user)
        form = QuestionForm()
        choice_formset = ChoiceFormSet()
        return render(request, self.template_name, {
            'form': form,
            'choice_formset': choice_formset,
            'exam': exam,
            'title': 'افزودن سوال'
        })

    def post(self, request, exam_pk):
        exam = get_object_or_404(Exam, pk=exam_pk, teacher=request.user)
        form = QuestionForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST)

        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()

            # If MCQ, save choices
            if question.qtype == Question.TYPE_MCQ:
                choice_formset = ChoiceFormSet(request.POST, instance=question)
                if choice_formset.is_valid():
                    choice_formset.save()

            messages.success(request, 'سوال با موفقیت اضافه شد.')
            return redirect('questions:exam_detail', pk=exam.pk)

        return render(request, self.template_name, {
            'form': form,
            'choice_formset': choice_formset,
            'exam': exam,
            'title': 'افزودن سوال'
        })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionUpdateView(View):
    template_name = 'questions/question_form.html'

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk, exam__teacher=request.user)
        form = QuestionForm(instance=question)
        choice_formset = ChoiceFormSet(instance=question)
        return render(request, self.template_name, {
            'form': form,
            'choice_formset': choice_formset,
            'exam': question.exam,
            'question': question,
            'title': 'ویرایش سوال'
        })

    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk, exam__teacher=request.user)
        form = QuestionForm(request.POST, instance=question)
        choice_formset = ChoiceFormSet(request.POST, instance=question)

        if form.is_valid():
            question = form.save()

            if question.qtype == Question.TYPE_MCQ and choice_formset.is_valid():
                choice_formset.save()

            messages.success(request, 'سوال با موفقیت به‌روزرسانی شد.')
            return redirect('questions:exam_detail', pk=question.exam.pk)

        return render(request, self.template_name, {
            'form': form,
            'choice_formset': choice_formset,
            'exam': question.exam,
            'question': question,
            'title': 'ویرایش سوال'
        })


@method_decorator([login_required, teacher_required], name='dispatch')
class QuestionDeleteView(View):
    template_name = 'questions/question_confirm_delete.html'

    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk, exam__teacher=request.user)
        return render(request, self.template_name, {'question': question})

    def post(self, request, pk):
        question = get_object_or_404(Question, pk=pk, exam__teacher=request.user)
        exam_pk = question.exam.pk
        question.delete()
        messages.success(request, 'سوال با موفقیت حذف شد.')
        return redirect('questions:exam_detail', pk=exam_pk)