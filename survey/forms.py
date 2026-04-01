from django import forms
from .models import Participant, Question, Answer


class ParticipantForm(forms.ModelForm):
    """نموذج تسجيل بيانات المشارك"""
    
    class Meta:
        model = Participant
        fields = ['name', 'gender', 'age', 'college', 'year', 
                  'primary_website', 'other_website', 
                  'computer_skill', 'daily_hours', 'other_hours']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم (اختياري)',
                'dir': 'rtl'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
                'dir': 'rtl'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثال: 21',
                'min': 17,
                'max': 35
            }),
            'college': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الكلية',
                'dir': 'rtl'
            }),
            'year': forms.Select(attrs={
                'class': 'form-select',
                'dir': 'rtl'
            }),
            'primary_website': forms.Select(attrs={
                'class': 'form-select',
                'dir': 'rtl'
            }),
            'other_website': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أذكر المواقع الأخرى إذا وجدت',
                'dir': 'rtl'
            }),
            'computer_skill': forms.Select(attrs={
                'class': 'form-select',
                'dir': 'rtl'
            }),
            'daily_hours': forms.Select(attrs={
                'class': 'form-select',
                'dir': 'rtl'
            }),
            'other_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أذكر عدد الساعات إذا كان مختلف',
                'dir': 'rtl'
            }),
        }
        
        labels = {
            'name': 'الاسم (اختياري)',
            'gender': 'النوع',
            'age': 'السن',
            'college': 'الكلية',
            'year': 'الفرقة الدراسية',
            'primary_website': 'أهم المواقع التي تستخدمها',
            'other_website': 'مواقع أخرى',
            'computer_skill': 'مهارة استخدام الحاسوب',
            'daily_hours': 'عدد الساعات اليومية التي تقضيها في تصفح الإنترنت',
            'other_hours': 'ساعات أخرى',
        }


class SurveyAnswerForm(forms.Form):
    """نموذج إجابات الاستبيان"""
    
    ANSWER_CHOICES = [
        ('yes', 'نعم'),
        ('somewhat', 'إلى حد ما'),
        ('no', 'لا'),
    ]
    
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions', [])
        super().__init__(*args, **kwargs)
        
        # إنشاء حقل لكل سؤال
        for question in questions:
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                choices=self.ANSWER_CHOICES,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                label=question.text,
                required=True
            )


class QuestionForm(forms.ModelForm):
    """نموذج إضافة/تعديل سؤال"""
    
    class Meta:
        model = Question
        fields = ['text', 'category', 'order', 'is_active']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'dir': 'rtl',
                'placeholder': 'أدخل نص السؤال هنا'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'dir': 'rtl'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'text': 'نص السؤال',
            'category': 'التصنيف',
            'order': 'الترتيب',
            'is_active': 'نشط',
        }
