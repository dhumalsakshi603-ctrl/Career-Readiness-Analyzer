from django.urls import path
from . import views

urlpatterns = [
    # Profile
    path("profile/", views.profile_view, name="profile"),

    # Resume
    path("resume/upload/", views.upload_resume_view, name="upload_resume"),
    path("resume/list/", views.list_resumes_view, name="list_resumes"),
    path("resume/latest/", views.latest_resume_view, name="latest_resume"),

    # Quiz
    path("quizzes/", views.list_quizzes_view, name="list_quizzes"),
    path("quiz/generate/", views.generate_quiz_view, name="generate_quiz"),
    path("quiz/<int:quiz_id>/", views.get_quiz_view, name="get_quiz"),
    path("quiz/<int:quiz_id>/submit/", views.submit_quiz_view, name="submit_quiz"),

    # Readiness / Progress
    path("readiness/calculate/", views.calculate_readiness_view, name="calculate_readiness"),
    path("readiness/history/", views.readiness_history_view, name="readiness_history"),
    path("readiness/latest/", views.latest_readiness_view, name="latest_readiness"),
]
