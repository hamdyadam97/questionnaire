from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Participant(models.Model):
    """نموذج المشارك في الاستبيان"""
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    YEAR_CHOICES = [
        ('1', 'الفرقة الأولى'),
        ('2', 'الفرقة الثانية'),
        ('3', 'الفرقة الثالثة'),
        ('4', 'الفرقة الرابعة'),
    ]
    
    WEBSITE_CHOICES = [
        ('sports', 'الرياضية'),
        ('entertainment', 'الفنية'),
        ('educational', 'التعليمية'),
        ('political', 'السياسية'),
        ('other', 'أخرى'),
    ]
    
    COMPUTER_SKILL_CHOICES = [
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
    ]
    
    HOURS_CHOICES = [
        ('less_than_1', 'أقل من ساعة'),
        ('1_to_2', 'من ساعة إلى ساعتين'),
        ('3_to_4', 'من ثلاثة ساعات إلى أربعة ساعات'),
        ('5_to_6', 'من خمس ساعات إلى ستة ساعات'),
        ('more', 'أكثر من ذلك'),
    ]
    
    # البيانات الأساسية
    name = models.CharField(max_length=100, verbose_name="الاسم (اختياري)", blank=True, null=True)
    email = models.EmailField(max_length=150, verbose_name="البريد الإلكتروني", blank=True, null=True)
    university = models.CharField(max_length=150, verbose_name="الجامعة", blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="النوع")
    age = models.PositiveIntegerField(verbose_name="السن", validators=[MinValueValidator(17), MaxValueValidator(35)])
    college = models.CharField(max_length=100, verbose_name="الكلية")
    year = models.CharField(max_length=1, choices=YEAR_CHOICES, verbose_name="الفرقة الدراسية")
    
    # المواقع المستخدمة
    primary_website = models.CharField(max_length=20, choices=WEBSITE_CHOICES, verbose_name="أهم المواقع المستخدمة")
    other_website = models.CharField(max_length=100, verbose_name="مواقع أخرى", blank=True, null=True)
    
    # مهارة استخدام الحاسوب
    computer_skill = models.CharField(max_length=15, choices=COMPUTER_SKILL_CHOICES, verbose_name="مهارة استخدام الحاسوب")
    
    # عدد الساعات اليومية
    daily_hours = models.CharField(max_length=15, choices=HOURS_CHOICES, verbose_name="عدد الساعات اليومية")
    other_hours = models.CharField(max_length=100, verbose_name="ساعات أخرى", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ المشاركة")
    
    class Meta:
        verbose_name = "مشارك"
        verbose_name_plural = "المشاركون"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_gender_display()} - {self.college} - {self.get_year_display()}"


class Question(models.Model):
    """نموذج السؤال في الاستبيان"""
    CATEGORY_CHOICES = [
        ('internet_usage_goal', 'الهدف من استخدام الإنترنت'),
        ('isolation_reality', 'واقع تفشي ظاهرة العزلة الإلكترونية'),
        ('academic_impact', 'تأثير العزلة الإلكترونية على التحصيل الدراسي'),
        ('social_impact', 'تأثير العزلة الإلكترونية على العلاقات الاجتماعية'),
        ('psychological_impact', 'تأثير العزلة الإلكترونية على الحالة النفسية'),
        ('suggestions', 'المقترحات للتخفيف من الآثار السلبية'),
    ]
    
    text = models.TextField(verbose_name="نص السؤال")
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES, verbose_name="التصنيف")
    order = models.PositiveIntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.text[:50]}..."


class Answer(models.Model):
    """نموذج الإجابة على السؤال"""
    ANSWER_CHOICES = [
        ('yes', 'نعم'),
        ('somewhat', 'إلى حد ما'),
        ('no', 'لا'),
    ]
    
    participant = models.ForeignKey(
        Participant, 
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="المشارك"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="السؤال"
    )
    answer = models.CharField(
        max_length=10,
        choices=ANSWER_CHOICES,
        verbose_name="الإجابة"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "إجابة"
        verbose_name_plural = "الإجابات"
        unique_together = ['participant', 'question']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.participant} - {self.question.text[:30]}... - {self.get_answer_display()}"


class SurveyResult(models.Model):
    """نموذج لحفظ نتائج الاستبيان المحسوبة"""
    category = models.CharField(max_length=25, choices=Question.CATEGORY_CHOICES, verbose_name="التصنيف")
    total_answers = models.PositiveIntegerField(default=0, verbose_name="إجمالي الإجابات")
    yes_count = models.PositiveIntegerField(default=0, verbose_name="عدد نعم")
    somewhat_count = models.PositiveIntegerField(default=0, verbose_name="عدد إلى حد ما")
    no_count = models.PositiveIntegerField(default=0, verbose_name="عدد لا")
    yes_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="نسبة نعم")
    somewhat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="نسبة إلى حد ما")
    no_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="نسبة لا")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")
    
    class Meta:
        verbose_name = "نتيجة الاستبيان"
        verbose_name_plural = "نتائج الاستبيان"
    
    def __str__(self):
        return f"نتائج: {self.get_category_display()}"
    
    def calculate_percentages(self):
        """حساب النسب المئوية"""
        if self.total_answers > 0:
            self.yes_percentage = (self.yes_count / self.total_answers) * 100
            self.somewhat_percentage = (self.somewhat_count / self.total_answers) * 100
            self.no_percentage = (self.no_count / self.total_answers) * 100
        else:
            self.yes_percentage = 0
            self.somewhat_percentage = 0
            self.no_percentage = 0
        self.save()
