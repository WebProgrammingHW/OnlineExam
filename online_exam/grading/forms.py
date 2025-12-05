# grading/forms.py
from django import forms
from .models import ManualReview
from attempts.models import Answer


class GradeAnswerForm(forms.Form):
    """Form for grading a single answer"""
    score = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'نمره',
            'step': '0.25'
        }),
        label='نمره'
    )
    comments = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'توضیحات (اختیاری)',
            'rows': 2
        }),
        required=False,
        label='توضیحات'
    )

    def __init__(self, *args, max_score=None, **kwargs):
        super().__init__(*args, **kwargs)
        if max_score:
            self.fields['score'].max_value = max_score
            self.fields['score'].widget.attrs['max'] = max_score


class ManualReviewForm(forms.ModelForm):
    class Meta:
        model = ManualReview
        fields = ['final_score', 'comments']
        widgets = {
            'final_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'final_score': 'نمره نهایی',
            'comments': 'توضیحات',
        }


class BulkGradeForm(forms.Form):
    """Form for bulk grading multiple answers"""
    pass  # Will be dynamically generated based on answers