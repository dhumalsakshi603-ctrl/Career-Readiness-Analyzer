from django.contrib import admin
from .models import (
    StudentProfile, Resume, ResumeAnalysis, Quiz, Question, Attempt, ReadinessAssessment,
)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "education", "target_role", "updated_at"]


class ResumeAnalysisInline(admin.StackedInline):
    model = ResumeAnalysis
    extra = 0


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "uploaded_at"]
    inlines = [ResumeAnalysisInline]


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "title", "topic", "difficulty", "created_at"]
    inlines = [QuestionInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "quiz", "score", "total_questions", "created_at"]


@admin.register(ReadinessAssessment)
class ReadinessAssessmentAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "overall_score", "target_role", "created_at"]
