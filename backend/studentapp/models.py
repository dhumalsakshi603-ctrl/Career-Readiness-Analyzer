from django.db import models
from django.contrib.auth.models import User


def resume_upload_path(instance, filename):
    return f"resumes/user_{instance.user.id}/{filename}"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True)
    education = models.CharField(max_length=255, blank=True)  # e.g. "BCA"
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    interests = models.TextField(blank=True, help_text="Comma-separated interests")
    target_role = models.CharField(max_length=255, blank=True, help_text="e.g. Backend Developer")
    updated_at = models.DateTimeField(auto_now=True)

    def skills_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def interests_list(self):
        return [s.strip() for s in self.interests.split(",") if s.strip()]

    def __str__(self):
        return f"Profile of {self.user.username}"


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="resumes")
    file = models.FileField(upload_to=resume_upload_path)
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume #{self.id} - {self.user.username}"


class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name="analysis")
    summary = models.TextField(blank=True)
    extracted_skills = models.JSONField(default=list)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis of Resume #{self.resume_id}"


class Quiz(models.Model):
    DIFFICULTY_CHOICES = [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default="medium")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.topic})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.PositiveSmallIntegerField()  # 0-3

    def __str__(self):
        return self.text[:60]


class Attempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attempts")
    quiz = models.ForeignKey(Quiz, related_name="attempts", on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)
    score = models.FloatField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    ai_feedback = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attempt #{self.id} - Quiz {self.quiz_id} - {self.score}/{self.total_questions}"


class ReadinessAssessment(models.Model):
    """One snapshot of a student's overall career readiness at a point in time.
    Used both for the dashboard result AND for the progress tracker history."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessments")
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, blank=True)
    attempt = models.ForeignKey(Attempt, on_delete=models.SET_NULL, null=True, blank=True)

    overall_score = models.FloatField(default=0)  # 0-100
    profile_score = models.FloatField(default=0)
    resume_score = models.FloatField(default=0)
    quiz_score = models.FloatField(default=0)

    skill_gaps = models.JSONField(default=list)  # [{skill, importance, current_level, note}]
    roadmap = models.JSONField(default=list)  # [{topic, resource_suggestion, priority}]
    feedback_summary = models.TextField(blank=True)

    target_role = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Assessment #{self.id} - {self.user.username} - {self.overall_score}"
