from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Participant, Question, Answer, SurveyResult
from .forms import ParticipantForm, QuestionForm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64


def home(request):
    """الصفحة الرئيسية"""
    context = {
        'total_participants': Participant.objects.count(),
        'total_questions': Question.objects.filter(is_active=True).count(),
        'total_answers': Answer.objects.count(),
    }
    return render(request, 'survey/home.html', context)


def survey_start(request):
    """صفحة بدء الاستبيان - تسجيل بيانات المشارك"""
    if request.method == 'POST':
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save()
            request.session['participant_id'] = participant.id
            messages.success(request, 'تم تسجيل بياناتك بنجاح! يرجى الإجابة على الأسئلة التالية.')
            return redirect('survey_questions')
    else:
        form = ParticipantForm()
    
    return render(request, 'survey/survey_start.html', {'form': form})


def survey_questions(request):
    """صفحة أسئلة الاستبيان"""
    participant_id = request.session.get('participant_id')
    if not participant_id:
        messages.warning(request, 'يرجى تسجيل بياناتك أولاً')
        return redirect('survey_start')
    
    participant = get_object_or_404(Participant, id=participant_id)
    
    # جلب الأسئلة مرتبة حسب التصنيف
    categories = [
        ('internet_usage_goal', 'الهدف من استخدام الإنترنت'),
        ('isolation_reality', 'واقع تفشي ظاهرة العزلة الإلكترونية'),
        ('academic_impact', 'تأثير العزلة الإلكترونية على التحصيل الدراسي'),
        ('social_impact', 'تأثير العزلة الإلكترونية على العلاقات الاجتماعية'),
        ('psychological_impact', 'تأثير العزلة الإلكترونية على الحالة النفسية'),
        ('suggestions', 'المقترحات للتخفيف من الآثار السلبية'),
    ]
    
    questions_by_category = {}
    for cat_key, cat_name in categories:
        questions = Question.objects.filter(category=cat_key, is_active=True).order_by('order')
        if questions.exists():
            questions_by_category[cat_name] = questions
    
    if not questions_by_category:
        messages.info(request, 'لا توجد أسئلة متاحة حالياً')
        return redirect('home')
    
    if request.method == 'POST':
        all_answered = True
        for cat_name, questions in questions_by_category.items():
            for question in questions:
                answer_key = f'question_{question.id}'
                answer_value = request.POST.get(answer_key)
                
                if answer_value:
                    Answer.objects.update_or_create(
                        participant=participant,
                        question=question,
                        defaults={'answer': answer_value}
                    )
                else:
                    all_answered = False
        
        if all_answered:
            update_survey_results()
            del request.session['participant_id']
            messages.success(request, 'شكراً لمشاركتك! تم حفظ إجاباتك بنجاح.')
            return redirect('survey_thanks')
        else:
            messages.error(request, 'يرجى الإجابة على جميع الأسئلة')
    
    # التحقق من الإجابات السابقة
    existing_answers = Answer.objects.filter(participant=participant)
    existing_answers_dict = {f'question_{ans.question.id}': ans.answer for ans in existing_answers}
    
    context = {
        'questions_by_category': questions_by_category,
        'participant': participant,
        'existing_answers': existing_answers_dict,
    }
    return render(request, 'survey/survey_questions.html', context)


def survey_thanks(request):
    """صفحة الشكر بعد إكمال الاستبيان"""
    return render(request, 'survey/survey_thanks.html')


def dashboard(request):
    """لوحة تحكم عرض النتائج"""
    # إحصائيات عامة
    total_participants = Participant.objects.count()
    total_questions = Question.objects.filter(is_active=True).count()
    total_answers = Answer.objects.count()
    
    # إحصائيات حسب النوع
    male_count = Participant.objects.filter(gender='male').count()
    female_count = Participant.objects.filter(gender='female').count()
    
    # إحصائيات حسب الفرقة
    year_stats = []
    for year_key, year_name in Participant.YEAR_CHOICES:
        count = Participant.objects.filter(year=year_key).count()
        year_stats.append({'name': year_name, 'count': count})
    
    # إحصائيات حسب عدد الساعات
    hours_stats = []
    for hours_key, hours_name in Participant.HOURS_CHOICES:
        count = Participant.objects.filter(daily_hours=hours_key).count()
        hours_stats.append({'name': hours_name, 'count': count})
    
    # نتائج الأسئلة حسب التصنيف مع تفاصيل كل سؤال
    categories = [
        ('internet_usage_goal', 'الهدف من استخدام الإنترنت'),
        ('isolation_reality', 'واقع تفشي ظاهرة العزلة الإلكترونية'),
        ('academic_impact', 'تأثير العزلة الإلكترونية على التحصيل الدراسي'),
        ('social_impact', 'تأثير العزلة الإلكترونية على العلاقات الاجتماعية'),
        ('psychological_impact', 'تأثير العزلة الإلكترونية على الحالة النفسية'),
        ('suggestions', 'المقترحات للتخفيف من الآثار السلبية'),
    ]
    
    category_results = []
    for cat_key, cat_name in categories:
        questions = Question.objects.filter(category=cat_key, is_active=True).order_by('order')
        
        # إحصائيات القسم الكلية
        all_answers = Answer.objects.filter(question__in=questions)
        total_cat_answers = all_answers.count()
        
        cat_data = {
            'category': cat_name,
            'cat_key': cat_key,
            'total': total_cat_answers,
            'questions': []
        }
        
        if total_cat_answers > 0:
            cat_data['yes_pct'] = round((all_answers.filter(answer='yes').count() / total_cat_answers) * 100, 2)
            cat_data['somewhat_pct'] = round((all_answers.filter(answer='somewhat').count() / total_cat_answers) * 100, 2)
            cat_data['no_pct'] = round((all_answers.filter(answer='no').count() / total_cat_answers) * 100, 2)
        
        # إحصائيات كل سؤال على حدة
        for idx, question in enumerate(questions, 1):
            q_answers = Answer.objects.filter(question=question)
            total_q = q_answers.count()
            
            if total_q > 0:
                yes_q = q_answers.filter(answer='yes').count()
                somewhat_q = q_answers.filter(answer='somewhat').count()
                no_q = q_answers.filter(answer='no').count()
                
                question_data = {
                    'number': idx,
                    'text': question.text,
                    'total': total_q,
                    'yes_count': yes_q,
                    'somewhat_count': somewhat_q,
                    'no_count': no_q,
                    'yes_pct': round((yes_q / total_q) * 100, 2),
                    'somewhat_pct': round((somewhat_q / total_q) * 100, 2),
                    'no_pct': round((no_q / total_q) * 100, 2),
                }
                cat_data['questions'].append(question_data)
        
        category_results.append(cat_data)
    
    # إنشاء الرسوم البيانية (Bar Charts لكل تصنيف)
    charts = generate_bar_charts_by_category(categories)
    
    context = {
        'total_participants': total_participants,
        'total_questions': total_questions,
        'total_answers': total_answers,
        'male_count': male_count,
        'female_count': female_count,
        'year_stats': year_stats,
        'hours_stats': hours_stats,
        'category_results': category_results,
        'charts': charts,
    }
    return render(request, 'survey/dashboard.html', context)


def generate_category_charts(category_results):
    """إنشاء الرسوم البيانية للتصنيفات"""
    charts = []
    
    for result in category_results:
        fig, ax = plt.subplots(figsize=(8, 5))
        
        labels = ['نعم', 'إلى حد ما', 'لا']
        sizes = [result['yes_pct'], result['somewhat_pct'], result['no_pct']]
        colors = ['#27ae60', '#f39c12', '#e74c3c']
        explode = (0.05, 0, 0)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.axis('equal')
        ax.set_title(result['category'], fontsize=12, fontweight='bold', pad=20)
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        charts.append({
            'category': result['category'],
            'chart': graphic,
            'data': result
        })
    
    return charts


def generate_bar_charts_by_category(categories):
    """إنشاء Bar Charts لكل تصنيف يعرض كل الأسئلة"""
    import numpy as np
    import matplotlib.font_manager as fm
    
    # البحث عن خط عربي متاح في النظام
    arabic_font = None
    system_fonts = fm.findSystemFonts(fontpaths=None, fontext='ttf')
    
    for font_path in system_fonts:
        try:
            prop = fm.FontProperties(fname=font_path)
            font_name = prop.get_name()
            # تجربة الخط على نص عربي
            if any(keyword in font_path.lower() for keyword in ['arial', 'tahoma', 'segoe', 'arialuni', 'noto', 'freesans']):
                arabic_font = prop
                break
        except:
            continue
    
    # إذا لم نجد خط عربي، نستخدم DejaVu Sans (لن يظهر العربي)
    if arabic_font is None:
        arabic_font = fm.FontProperties(family='DejaVu Sans')
    
    charts = []
    
    for cat_key, cat_name in categories:
        questions = Question.objects.filter(category=cat_key, is_active=True).order_by('order')
        
        if not questions.exists():
            continue
        
        # جمع بيانات كل سؤال
        question_labels = []
        yes_counts = []
        no_counts = []
        somewhat_counts = []
        
        for i, q in enumerate(questions, 1):
            # استخدام أرقام للأسئلة بدلاً من النص الكامل
            question_labels.append(f'س{i}')
            
            answers = Answer.objects.filter(question=q)
            yes_counts.append(answers.filter(answer='yes').count())
            no_counts.append(answers.filter(answer='no').count())
            somewhat_counts.append(answers.filter(answer='somewhat').count())
        
        if not any(yes_counts + no_counts + somewhat_counts):
            continue
        
        # إنشاء الرسم البياني
        fig, ax = plt.subplots(figsize=(14, 7))
        
        x = np.arange(len(question_labels))
        width = 0.25
        
        # حساب النسب المئوية لكل سؤال
        yes_pcts = []
        no_pcts = []
        somewhat_pcts = []
        
        for i in range(len(yes_counts)):
            total = yes_counts[i] + no_counts[i] + somewhat_counts[i]
            if total > 0:
                yes_pcts.append(round((yes_counts[i] / total) * 100, 1))
                no_pcts.append(round((no_counts[i] / total) * 100, 1))
                somewhat_pcts.append(round((somewhat_counts[i] / total) * 100, 1))
            else:
                yes_pcts.append(0)
                no_pcts.append(0)
                somewhat_pcts.append(0)
        
        # الألوان مطابقة للصورة (أزرق = نعم، برتقالي = لا، أصفر = إلى حد ما)
        bars1 = ax.bar(x - width, yes_counts, width, label='Yes', color='#4472C4')
        bars2 = ax.bar(x, no_counts, width, label='No', color='#ED7D31')
        bars3 = ax.bar(x + width, somewhat_counts, width, label='Somewhat', color='#FFC000')
        
        # إضافة النسب المئوية فوق الأعمدة
        def add_percentage_labels(bars, percentages, counts):
            for bar, pct, count in zip(bars, percentages, counts):
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                           f'{pct}%\n({count})',
                           ha='center', va='bottom', fontsize=7, fontweight='bold')
        
        add_percentage_labels(bars1, yes_pcts, yes_counts)
        add_percentage_labels(bars2, no_pcts, no_counts)
        add_percentage_labels(bars3, somewhat_pcts, somewhat_counts)
        
        # إعدادات المحاور
        ax.set_ylabel('Count', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(question_labels, fontsize=10)
        
        # تعديل حدود المحور Y لإفساح مجال للنصوص
        ax.set_ylim(0, max(max(yes_counts), max(no_counts), max(somewhat_counts)) * 1.2)
        
        # legend بالإنجليزية
        ax.legend(loc='upper right', fontsize=10)
        
        # شبكة أفقية
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        ax.set_axisbelow(True)
        
        # ضبط المسافات
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        graphic = base64.b64encode(image_png).decode('utf-8')
        
        # إنشاء قائمة الأسئلة مع أرقامها
        question_list = []
        for i, q in enumerate(questions, 1):
            question_list.append({
                'number': f'س{i}',
                'text': q.text
            })
        
        charts.append({
            'category': cat_name,
            'chart': graphic,
            'data': {
                'yes_count': sum(yes_counts),
                'no_count': sum(no_counts),
                'somewhat_count': sum(somewhat_counts),
            },
            'questions': question_list
        })
    
    return charts


def update_survey_results():
    """تحديث نتائج الاستبيان"""
    categories = [
        'internet_usage_goal',
        'isolation_reality',
        'academic_impact',
        'social_impact',
        'psychological_impact',
        'suggestions',
    ]
    
    for cat_key in categories:
        questions = Question.objects.filter(category=cat_key)
        answers = Answer.objects.filter(question__in=questions)
        total = answers.count()
        
        if total > 0:
            yes_count = answers.filter(answer='yes').count()
            somewhat_count = answers.filter(answer='somewhat').count()
            no_count = answers.filter(answer='no').count()
            
            result, created = SurveyResult.objects.get_or_create(category=cat_key)
            result.total_answers = total
            result.yes_count = yes_count
            result.somewhat_count = somewhat_count
            result.no_count = no_count
            result.calculate_percentages()


def participants_list(request):
    """قائمة المشاركين"""
    participants = Participant.objects.prefetch_related('answers').all()
    return render(request, 'survey/participants_list.html', {'participants': participants})


def questions_management(request):
    """إدارة الأسئلة"""
    questions = Question.objects.all().order_by('order')
    return render(request, 'survey/questions_management.html', {'questions': questions})


def add_question(request):
    """إضافة سؤال جديد"""
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة السؤال بنجاح')
            return redirect('questions_management')
    else:
        form = QuestionForm()
    
    return render(request, 'survey/question_form.html', {'form': form, 'action': 'إضافة'})


def edit_question(request, question_id):
    """تعديل سؤال"""
    question = get_object_or_404(Question, id=question_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث السؤال بنجاح')
            return redirect('questions_management')
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'survey/question_form.html', {'form': form, 'action': 'تعديل'})


def delete_question(request, question_id):
    """حذف سؤال"""
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    messages.success(request, 'تم حذف السؤال بنجاح')
    return redirect('questions_management')


# API Views
@require_http_methods(["GET"])
def api_survey_stats(request):
    """API للحصول على إحصائيات الاستبيان"""
    stats = {
        'total_participants': Participant.objects.count(),
        'total_questions': Question.objects.filter(is_active=True).count(),
        'total_answers': Answer.objects.count(),
    }
    return JsonResponse(stats)


@require_http_methods(["GET"])
def api_category_results(request, category):
    """API للحصول على نتائج تصنيف محدد"""
    questions = Question.objects.filter(category=category, is_active=True)
    answers = Answer.objects.filter(question__in=questions)
    total = answers.count()
    
    if total > 0:
        data = {
            'category': category,
            'total_answers': total,
            'yes_count': answers.filter(answer='yes').count(),
            'somewhat_count': answers.filter(answer='somewhat').count(),
            'no_count': answers.filter(answer='no').count(),
        }
        data['yes_percentage'] = round((data['yes_count'] / total) * 100, 2)
        data['somewhat_percentage'] = round((data['somewhat_count'] / total) * 100, 2)
        data['no_percentage'] = round((data['no_count'] / total) * 100, 2)
    else:
        data = {
            'category': category,
            'total_answers': 0,
            'yes_count': 0,
            'somewhat_count': 0,
            'no_count': 0,
            'yes_percentage': 0,
            'somewhat_percentage': 0,
            'no_percentage': 0,
        }
    
    return JsonResponse(data)
