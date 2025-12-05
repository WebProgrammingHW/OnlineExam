# attempts/forms.py
from django import forms
from .models import Answer
from questions.models import Question, Choice


class ShortAnswerForm(forms.Form):
    """Form for short answer questions"""
    answer = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'پاسخ خود را بنویسید...',
            'rows': 3
        }),
        required=False
    )


class MCQAnswerForm(forms.Form):
    """Form for multiple choice questions"""
    choice = forms.ModelChoiceField(
        queryset=Choice.objects.none(),
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        empty_label=None
    )

    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            self.fields['choice'].queryset = question.choices.all()


class FileAnswerForm(forms.Form):
    """Form for file upload questions"""
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }),
        required=False
    )


class AnswerForm(forms.ModelForm):
    """Generic answer form"""
    class Meta:
        model = Answer
        fields = ['text_answer', 'selected_choice', 'uploaded_file']
        widgets = {
            'text_answer': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'selected_choice': forms.RadioSelect(),
            'uploaded_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            if question.qtype == Question.TYPE_MCQ:
                self.fields['selected_choice'].queryset = question.choices.all()
            else:
                self.fields['selected_choice'].queryset = Choice.objects.none()