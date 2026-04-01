from django.contrib import admin
from .models import Participant, Question, Answer, SurveyResult


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'gender', 'age', 'college', 'year', 'daily_hours', 'created_at']
    list_filter = ['gender', 'year', 'daily_hours', 'computer_skill', 'primary_website', 'created_at']
    search_fields = ['name', 'college', 'other_website']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('البيانات الأساسية', {
            'fields': ('name', 'gender', 'age', 'college', 'year')
        }),
        ('استخدام الإنترنت', {
            'fields': ('primary_website', 'other_website', 'computer_skill', 'daily_hours', 'other_hours')
        }),
        ('معلومات إضافية', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text_short', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['text']
    list_editable = ['order', 'is_active']
    ordering = ['order', 'created_at']
    
    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_short.short_description = 'نص السؤال'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['participant_info', 'question_short', 'get_answer_display', 'created_at']
    list_filter = ['answer', 'created_at', 'question__category']
    search_fields = ['participant__name', 'participant__college', 'question__text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def participant_info(self, obj):
        return f"{obj.participant.get_gender_display()} - {obj.participant.college}"
    participant_info.short_description = 'المشارك'
    
    def question_short(self, obj):
        return obj.question.text[:40] + '...' if len(obj.question.text) > 40 else obj.question.text
    question_short.short_description = 'السؤال'


@admin.register(SurveyResult)
class SurveyResultAdmin(admin.ModelAdmin):
    list_display = ['get_category_display', 'total_answers', 'yes_count', 'somewhat_count', 'no_count', 
                    'yes_percentage', 'somewhat_percentage', 'no_percentage', 'updated_at']
    list_filter = ['updated_at']
    readonly_fields = ['total_answers', 'yes_count', 'somewhat_count', 'no_count', 
                       'yes_percentage', 'somewhat_percentage', 'no_percentage', 'updated_at']
    ordering = ['-updated_at']
