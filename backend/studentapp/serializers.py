from rest_framework import serializers
from .models import StudentProfile, Resume, ResumeAnalysis, Quiz, Question, Attempt, ReadinessAssessment


class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = [
            "id", "full_name", "education", "graduation_year",
            "skills", "interests", "target_role", "updated_at",
        ]


class ResumeAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = ["summary", "extracted_skills", "strengths", "weaknesses", "created_at"]


class ResumeSerializer(serializers.ModelSerializer):
    analysis = ResumeAnalysisSerializer(read_only=True)

    class Meta:
        model = Resume
        fields = ["id", "file", "uploaded_at", "analysis"]


class QuestionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text", "option_a", "option_b", "option_c", "option_d"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "topic", "difficulty", "created_at", "questions"]


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id", "title", "topic", "difficulty", "created_at"]


class AttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attempt
        fields = ["id", "quiz", "answers", "score", "total_questions", "ai_feedback", "created_at"]
        read_only_fields = ["score", "total_questions", "ai_feedback"]


class ReadinessAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadinessAssessment
        fields = [
            "id", "overall_score", "profile_score", "resume_score", "quiz_score",
            "skill_gaps", "roadmap", "feedback_summary", "target_role", "created_at",
        ]
