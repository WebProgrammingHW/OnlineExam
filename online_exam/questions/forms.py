# questions/forms.py
from django import forms
from .models import Exam, Question, Choice


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'topic', 'start_at', 
                  'duration_minutes', 'total_score', 'published']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان آزمون'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'توضیحات آزمون',
                'rows': 3
            }),
            'topic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع آزمون'
            }),
            'start_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مدت زمان (دقیقه)'
            }),
            'total_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'نمره کل'
            }),
            'published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'عنوان آزمون',
            'description': 'توضیحات',
            'topic': 'موضوع',
            'start_at': 'زمان شروع',
            'duration_minutes': 'مدت زمان (دقیقه)',
            'total_score': 'نمره کل',
            'published': 'منتشر شده',
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'qtype', 'max_score', 'auto_grade_regex', 'order']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'متن سوال',
                'rows': 3
            }),
            'qtype': forms.Select(attrs={
                'class': 'form-control',
                'id': 'question-type-select'
            }),
            'max_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'نمره سوال'
            }),
            'auto_grade_regex': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'پاسخ صحیح (برای نمره‌دهی خودکار)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ترتیب'
            }),
        }
        labels = {
            'text': 'متن سوال',
            'qtype': 'نوع سوال',
            'max_score': 'نمره',
            'auto_grade_regex': 'پاسخ صحیح',
            'order': 'ترتیب',
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'متن گزینه'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ترتیب'
            }),
        }
        labels = {
            'text': 'متن گزینه',
            'is_correct': 'گزینه صحیح',
            'order': 'ترتیب',
        }


# Formset for multiple choices
ChoiceFormSet = forms.inlineformset_factory(
    Question,
    Choice,
    form=ChoiceForm,
    extra=4,
    can_delete=True,
    min_num=2,
    validate_min=True
)