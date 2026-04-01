#!/usr/bin/env python3
"""
سكربت لإنشاء بيانات تجريبية للاستبيان
"""
import os
import sys
import random

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isolation_survey.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from survey.models import Participant, Question, Answer


def create_sample_participants(count=100):
    """إنشاء مشاركين تجريبيين"""
    colleges = [
        'كلية الخدمة الاجتماعية',
        'كلية التربية',
        'كلية الآداب',
        'كلية العلوم',
        'كلية التجارة',
        'كلية الهندسة',
        'كلية الطب',
        'كلية الحقوق',
        'كلية الإعلام',
        'كلية الحاسبات',
    ]
    
    first_names_male = [
        'أحمد', 'محمد', 'خالد', 'عبدالله', 'سعد', 'فهد', 'سلطان', 'نواف',
        'عمر', 'علي', 'يوسف', 'إبراهيم', 'نايف', 'ماجد', 'تركي', 'بندر',
    ]
    
    first_names_female = [
        'سارة', 'نورة', 'فاطمة', 'هند', 'ريم', 'دانة', 'لمى', 'جود',
        'ليلى', 'رنا', 'مها', 'أمل', 'هدى', 'وجدان', 'شهد', 'رغد',
    ]
    
    last_names = [
        'الحربي', 'العتيبي', 'القحطاني', 'الغامدي', 'الشمري', 'السهلي',
        'الصالح', 'الفهد', 'الرشيد', 'المطيري', 'الدوسري', 'الشهراني',
        'البلوي', 'الخالدي', 'الهاجري', 'السويلم', 'المقبل', 'العنزي'
    ]
    
    created_count = 0
    
    for i in range(count):
        # اختيار النوع
        gender = random.choice(['male', 'female'])
        
        if gender == 'male':
            first_name = random.choice(first_names_male)
        else:
            first_name = random.choice(first_names_female)
        
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        
        # إنشاء المشارك
        participant = Participant.objects.create(
            name=name,
            gender=gender,
            age=random.randint(18, 26),
            college=random.choice(colleges),
            year=random.choice(['1', '2', '3', '4']),
            primary_website=random.choice(['sports', 'entertainment', 'educational', 'political', 'other']),
            computer_skill=random.choice(['beginner', 'intermediate', 'advanced']),
            daily_hours=random.choice(['less_than_1', '1_to_2', '3_to_4', '5_to_6', 'more']),
        )
        
        created_count += 1
        
        if created_count % 20 == 0:
            print(f"✓ تم إنشاء {created_count} مشارك...")
    
    print(f"\nتم إنشاء {created_count} مشارك جديد")
    return Participant.objects.all()


def create_sample_answers():
    """إنشاء إجابات تجريبية"""
    participants = Participant.objects.all()
    questions = Question.objects.filter(is_active=True)
    
    if not participants or not questions:
        print("لا يوجد مشاركين أو أسئلة لإنشاء الإجابات")
        return
    
    answer_choices = ['yes', 'somewhat', 'no']
    # توزيع مائل نحو الإجابات الإيجابية
    weights = [0.4, 0.35, 0.25]  # 40% نعم، 35% إلى حد ما، 25% لا
    
    created_count = 0
    for participant in participants:
        for question in questions:
            # اختيار إجابة عشوائية مع التوزيع المحدد
            answer = random.choices(answer_choices, weights=weights)[0]
            
            Answer.objects.get_or_create(
                participant=participant,
                question=question,
                defaults={'answer': answer}
            )
            created_count += 1
        
        if created_count % 500 == 0:
            print(f"✓ تم إنشاء {created_count} إجابة...")
    
    print(f"\nتم إنشاء {created_count} إجابة جديدة")


def main():
    print("=" * 60)
    print("إنشاء بيانات تجريبية للاستبيان")
    print("=" * 60)
    
    # إنشاء المشاركين
    print("\n1. إنشاء المشاركين...")
    create_sample_participants(100)
    
    # إنشاء الإجابات
    print("\n2. إنشاء الإجابات...")
    create_sample_answers()
    
    print("\n" + "=" * 60)
    print("تم إنشاء البيانات التجريبية بنجاح!")
    print("=" * 60)
    
    # عرض الإحصائيات
    print(f"\nإحصائيات النظام:")
    print(f"- عدد الأسئلة: {Question.objects.count()}")
    print(f"- عدد المشاركين: {Participant.objects.count()}")
    print(f"- عدد الإجابات: {Answer.objects.count()}")


if __name__ == '__main__':
    main()
