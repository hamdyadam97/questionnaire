#!/usr/bin/env python3
"""
سكربت لإنشاء أسئلة الاستبيان من الاستمارة
"""
import os
import sys

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isolation_survey.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from survey.models import Question


def create_questions():
    """إنشاء أسئلة الاستبيان من الاستمارة"""
    
    # الهدف من استخدام الإنترنت
    internet_usage_questions = [
        'الترفيه من خلال ممارسة الألعاب الإلكترونية',
        'الترفيه من خلال مشاهدة الأفلام',
        'البحث عن معلومات في مجال التخصص',
        'الاطلاع على الصحف',
        'التواصل عبر الشبكات الإلكترونية',
        'تصفح المنتديات',
    ]
    
    # واقع تفشي ظاهرة العزلة الإلكترونية
    isolation_reality_questions = [
        'أشعر أن الوقت الذي أقضيه في تصفح الإنترنت غير كافٍ',
        'أتناول بعض وجباتي أمام الإنترنت حتى لا أتوقف عن استخدامه',
        'أعود لاستخدام الإنترنت باستمرار بدون وعي بعد أن عزمت أن أقلل من استخدامي للإنترنت',
        'أشعر بالتوتر عند توقفي عن استخدام الإنترنت بسبب عطل مؤقت بالشبكة',
        'أجد في الإنترنت الإثارة التي لا أجدها في أي شيء آخر',
    ]
    
    # تأثير العزلة الإلكترونية على التحصيل الدراسي
    academic_impact_questions = [
        'عدم التركيز في دراستي بسبب حبي الشديد للإنترنت',
        'أهملت الدراسة بسبب انشغالي بالإنترنت',
        'يتيح لي الإنترنت المعرفة في أي مجال أكثر بكثير من الكتب الدراسية',
        'ألجأ لتصفح الإنترنت إذا واجهت صعوبة في دراستي',
        'كم ساعة تقضيها وسطياً على وسائل التواصل الاجتماعي يومياً',
    ]
    
    # تأثير العزلة الإلكترونية على العلاقات الاجتماعية
    social_impact_questions = [
        'أستمر في استخدام الإنترنت بشكل كبير رغم ما يسببه لي من مشكلات',
        'أفضل استخدام الإنترنت على الخروج مع أصدقائي',
        'أفضل استخدام الإنترنت على زيارة أقاربي',
        'تعرفت على أصدقاء كثيرين من خلال الإنترنت',
        'أشعر أن الأصدقاء المخلصين هم أصدقاء الإنترنت فقط',
        'أجد متعة في محادثة الآخرين على الإنترنت أكثر من محادثتهم وجهاً لوجه',
    ]
    
    # تأثير العزلة الإلكترونية على الحالة النفسية
    psychological_impact_questions = [
        'الإنترنت هو المكان الوحيد الذي أشعر فيه بالمتعة',
        'استخدامي للإنترنت يسيطر على تفكيري بدرجة كبيرة',
        'أشعر بالاكتئاب عندما لا أستخدم الإنترنت',
        'أستخدم الإنترنت للهروب من مشكلاتي',
        'أشعر بالراحة عندما أستخدم الإنترنت',
    ]
    
    # المقترحات
    suggestions_questions = [
        'عقد ندوات لتوعية الشباب الجامعي بالآثار السلبية المترتبة على العزلة الإلكترونية الناجمة عن استخدام الإنترنت',
        'زيادة عدد الأخصائيين الاجتماعيين بالجامعات لتوعية الطلاب بالآثار السلبية للعزلة الإلكترونية الناجمة عن استخدام الإنترنت',
        'تعزيز الوعي بكيفية الاستفادة من الإنترنت في البحث عن معلومات في مجال التخصص للاستفادة منها',
        'تفعيل دور الأخصائي الاجتماعي داخل الجماعات الطلابية لمواجهة الانسحاب الجماعي',
        'تعريف الشباب الجامعي بالآثار السلبية للاستخدام السلبي للإنترنت',
        'عقد ورش العمل لتدريب الشباب حول الاستخدام الآمن للإنترنت',
        'توفير أماكن لممارسة الأنشطة الطلابية الجماعية لشغل أوقات فراغهم',
    ]
    
    # إنشاء الأسئلة
    all_questions = [
        ('internet_usage_goal', internet_usage_questions),
        ('isolation_reality', isolation_reality_questions),
        ('academic_impact', academic_impact_questions),
        ('social_impact', social_impact_questions),
        ('psychological_impact', psychological_impact_questions),
        ('suggestions', suggestions_questions),
    ]
    
    created_count = 0
    order = 1
    
    for category, questions_list in all_questions:
        for q_text in questions_list:
            question, created = Question.objects.get_or_create(
                text=q_text,
                defaults={
                    'category': category,
                    'order': order,
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                print(f"✓ تم إنشاء السؤال: {q_text[:50]}...")
            order += 1
    
    print(f"\nتم إنشاء {created_count} سؤال جديد")
    return Question.objects.filter(is_active=True)


def main():
    print("=" * 60)
    print("إنشاء أسئلة استبيان العزلة الإلكترونية")
    print("=" * 60)
    
    create_questions()
    
    print("\n" + "=" * 60)
    print("تم إنشاء الأسئلة بنجاح!")
    print("=" * 60)
    
    # عرض الإحصائيات
    print(f"\nإحصائيات الأسئلة:")
    print(f"- إجمالي الأسئلة: {Question.objects.count()}")
    
    categories = [
        ('internet_usage_goal', 'الهدف من استخدام الإنترنت'),
        ('isolation_reality', 'واقع تفشي ظاهرة العزلة الإلكترونية'),
        ('academic_impact', 'تأثير العزلة الإلكترونية على التحصيل الدراسي'),
        ('social_impact', 'تأثير العزلة الإلكترونية على العلاقات الاجتماعية'),
        ('psychological_impact', 'تأثير العزلة الإلكترونية على الحالة النفسية'),
        ('suggestions', 'المقترحات للتخفيف من الآثار السلبية'),
    ]
    
    for cat_key, cat_name in categories:
        count = Question.objects.filter(category=cat_key).count()
        print(f"- {cat_name}: {count} سؤال")


if __name__ == '__main__':
    main()
