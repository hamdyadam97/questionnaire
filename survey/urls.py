from django.urls import path
from . import views

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.home, name='home'),
    path('survey/start/', views.survey_start, name='survey_start'),
    path('survey/questions/', views.survey_questions, name='survey_questions'),
    path('survey/thanks/', views.survey_thanks, name='survey_thanks'),
    
    # لوحة التحكم
    path('dashboard/', views.dashboard, name='dashboard'),
    path('participants/', views.participants_list, name='participants_list'),
    
    # إدارة الأسئلة
    path('questions/', views.questions_management, name='questions_management'),
    path('questions/add/', views.add_question, name='add_question'),
    path('questions/edit/<int:question_id>/', views.edit_question, name='edit_question'),
    path('questions/delete/<int:question_id>/', views.delete_question, name='delete_question'),
    
    # API
    path('api/stats/', views.api_survey_stats, name='api_survey_stats'),
    path('api/results/<str:category>/', views.api_category_results, name='api_category_results'),
]
