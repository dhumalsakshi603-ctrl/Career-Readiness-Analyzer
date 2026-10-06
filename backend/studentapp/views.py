from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StudentProfile, Resume, ResumeAnalysis, Quiz, Question, Attempt, ReadinessAssessment
from .serializers import (
    StudentProfileSerializer, ResumeSerializer, QuizSerializer, QuizListSerializer,
    ReadinessAssessmentSerializer,
)
from . import gemini_service, resume_parser


# ---------------------------------------------------------------------------
# Student Profile
# ---------------------------------------------------------------------------
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "GET":
        return Response(StudentProfileSerializer(profile).data)

    # PUT - update
    serializer = StudentProfileSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# Resume upload + Gemini analysis
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_resume_view(request):
    file_obj = request.FILES.get("file")
    if not file_obj:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    max_bytes = settings.MAX_RESUME_UPLOAD_SIZE_MB * 1024 * 1024
    if file_obj.size > max_bytes:
        return Response(
            {"error": f"File too large. Max size is {settings.MAX_RESUME_UPLOAD_SIZE_MB}MB."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    name_lower = file_obj.name.lower()
    if not (name_lower.endswith(".pdf") or name_lower.endswith(".docx")):
        return Response(
            {"error": "Only .pdf and .docx files are supported"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        extracted_text = resume_parser.extract_text_from_file(file_obj)
    except Exception as e:
        return Response(
            {"error": f"Could not read file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not extracted_text.strip():
        return Response(
            {"error": "Could not extract any text from this file. Is it a scanned/image-only PDF?"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    resume = Resume.objects.create(user=request.user, file=file_obj, extracted_text=extracted_text)

    profile = StudentProfile.objects.filter(user=request.user).first()
    target_role = profile.target_role if profile else ""

    try:
        analysis_data = gemini_service.analyze_resume(extracted_text, target_role)
    except Exception as e:
        return Response(
            {
                "error": f"Resume uploaded but AI analysis failed: {str(e)}",
                "resume_id": resume.id,
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    ResumeAnalysis.objects.create(
        resume=resume,
        summary=analysis_data["summary"],
        extracted_skills=analysis_data["extracted_skills"],
        strengths=analysis_data["strengths"],
        weaknesses=analysis_data["weaknesses"],
    )

    resume.refresh_from_db()
    return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_resumes_view(request):
    resumes = Resume.objects.filter(user=request.user).order_by("-uploaded_at")
    return Response(ResumeSerializer(resumes, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_resume_view(request):
    resume = Resume.objects.filter(user=request.user).order_by("-uploaded_at").first()
    if not resume:
        return Response({"resume": None})
    return Response(ResumeSerializer(resume).data)


# ---------------------------------------------------------------------------
# Quiz: generate / fetch / submit
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_quizzes_view(request):
    quizzes = Quiz.objects.filter(user=request.user).order_by("-created_at")
    return Response(QuizListSerializer(quizzes, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_quiz_view(request):
    topic = request.data.get("topic", "").strip()
    difficulty = request.data.get("difficulty", "medium")
    count = int(request.data.get("count", 5))

    if not topic:
        return Response({"error": "topic is required"}, status=status.HTTP_400_BAD_REQUEST)
    if count < 1 or count > 20:
        return Response({"error": "count must be between 1 and 20"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        questions_data = gemini_service.generate_mcq_questions(topic, difficulty, count)
    except Exception as e:
        return Response(
            {"error": f"Failed to generate questions from Gemini: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    quiz = Quiz.objects.create(user=request.user, title=f"{topic.title()} Quiz", topic=topic, difficulty=difficulty)
    for q in questions_data:
        Question.objects.create(
            quiz=quiz,
            text=q["text"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_option=int(q["correct_option"]),
        )

    return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_quiz_view(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, user=request.user)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(QuizSerializer(quiz).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_quiz_view(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id, user=request.user)
    except Quiz.DoesNotExist:
        return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    answers = request.data.get("answers", {})
    questions = quiz.questions.all()

    correct_count = 0
    wrong_question_texts = []
    for q in questions:
        selected = answers.get(str(q.id))
        if selected is not None and int(selected) == q.correct_option:
            correct_count += 1
        else:
            wrong_question_texts.append(q.text)

    total = questions.count()
    score = correct_count

    try:
        feedback = gemini_service.generate_quiz_feedback(quiz.topic, score, total, wrong_question_texts)
    except Exception as e:
        feedback = f"(AI feedback unavailable: {str(e)})"

    attempt = Attempt.objects.create(
        user=request.user, quiz=quiz, answers=answers, score=score,
        total_questions=total, ai_feedback=feedback,
    )

    review = [
    {
        "question_id": q.id,
        "text": q.text,
        "correct_option": q.correct_option,
        "selected_option": answers.get(str(q.id)),
        "is_correct": str(answers.get(str(q.id))) == str(q.correct_option)
    }
    for q in questions
]
    return Response(
        {
            "attempt_id": attempt.id,
            "score": score,
            "total_questions": total,
            "ai_feedback": feedback,
            "review": review,
        },
        status=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# Readiness Assessment (score + skill gap + roadmap) + Progress Tracker
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def calculate_readiness_view(request):
    """
    Combines: profile, latest resume analysis (optional), and a specific
    quiz attempt (optional, passed as attempt_id) into one readiness report.
    Body: { "attempt_id": <int, optional> }
    """
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    resume = Resume.objects.filter(user=request.user).order_by("-uploaded_at").first()

    resume_analysis_data = None
    if resume and hasattr(resume, "analysis"):
        resume_analysis_data = {
            "summary": resume.analysis.summary,
            "extracted_skills": resume.analysis.extracted_skills,
            "strengths": resume.analysis.strengths,
            "weaknesses": resume.analysis.weaknesses,
        }

    attempt_id = request.data.get("attempt_id")
    attempt = None
    quiz_topic = None
    quiz_score = None
    quiz_total = None
    if attempt_id:
        attempt = Attempt.objects.filter(id=attempt_id, user=request.user).first()
        if attempt:
            quiz_topic = attempt.quiz.topic
            quiz_score = attempt.score
            quiz_total = attempt.total_questions
    else:
        # fall back to most recent attempt if any
        attempt = Attempt.objects.filter(user=request.user).order_by("-created_at").first()
        if attempt:
            quiz_topic = attempt.quiz.topic
            quiz_score = attempt.score
            quiz_total = attempt.total_questions

    try:
        report = gemini_service.generate_readiness_report(
            target_role=profile.target_role,
            profile_skills=profile.skills_list(),
            profile_interests=profile.interests_list(),
            resume_analysis=resume_analysis_data,
            quiz_topic=quiz_topic,
            quiz_score=quiz_score,
            quiz_total=quiz_total,
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to generate readiness report: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    assessment = ReadinessAssessment.objects.create(
        user=request.user,
        resume=resume,
        attempt=attempt,
        overall_score=report["overall_score"],
        profile_score=report["profile_score"],
        resume_score=report["resume_score"],
        quiz_score=report["quiz_score"],
        skill_gaps=report["skill_gaps"],
        roadmap=report["roadmap"],
        feedback_summary=report["feedback_summary"],
        target_role=profile.target_role,
    )

    return Response(ReadinessAssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def readiness_history_view(request):
    """Progress tracker: all past readiness assessments, oldest to newest."""
    assessments = ReadinessAssessment.objects.filter(user=request.user).order_by("created_at")
    return Response(ReadinessAssessmentSerializer(assessments, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_readiness_view(request):
    assessment = ReadinessAssessment.objects.filter(user=request.user).order_by("-created_at").first()
    if not assessment:
        return Response({"assessment": None})
    return Response(ReadinessAssessmentSerializer(assessment).data)
