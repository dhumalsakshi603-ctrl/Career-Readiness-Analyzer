"""
All Gemini API calls live here:
1. generate_mcq_questions   - creates MCQ quiz for a topic/difficulty
2. generate_quiz_feedback   - short feedback paragraph after a quiz attempt
3. analyze_resume           - extracts skills/strengths/weaknesses from resume text
4. generate_readiness_report - combines profile + resume + quiz into an
                                overall score, skill gaps, and learning roadmap
"""
import json
import re
import time
from django.conf import settings
from google import genai
from google.genai import types


def _get_client():
    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _extract_json(text: str):
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    start_candidates = [i for i in (text.find("["), text.find("{")) if i != -1]
    if not start_candidates:
        raise ValueError("No JSON structure found in Gemini response")
    start = min(start_candidates)
    end_candidates = [i for i in (text.rfind("]"), text.rfind("}")) if i != -1]
    end = max(end_candidates) + 1
    return json.loads(text[start:end])


def _call_gemini(prompt: str, temperature: float = 0.7, json_mode: bool = True) -> str:
    client = _get_client()

    config_kwargs = {"temperature": temperature}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs),
            )
            return response.text

        except Exception as e:
            error_text = str(e)

            # Retry temporary Gemini server errors
            if "503" in error_text or "UNAVAILABLE" in error_text:
                if attempt < max_retries - 1:
                    wait_time = 5 * (2 ** attempt)
                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time} seconds..."
                    )
                    time.sleep(wait_time)
                    continue

            # For other errors, or if all retries fail
            raise


# ---------------------------------------------------------------------------
# 1. MCQ generation
# ---------------------------------------------------------------------------
def generate_mcq_questions(topic: str, difficulty: str = "medium", count: int = 5):
    prompt = f"""You are a quiz question generator.
Generate exactly {count} multiple-choice questions on the topic: "{topic}".
Difficulty level: {difficulty}.

Return ONLY a valid JSON array, no explanation, no markdown fences.
Each item must have this exact structure:
{{
  "text": "question text here",
  "option_a": "option A text",
  "option_b": "option B text",
  "option_c": "option C text",
  "option_d": "option D text",
  "correct_option": 0
}}
"correct_option" is an integer: 0=A, 1=B, 2=C, 3=D. Only one option is correct.
"""
    raw = _call_gemini(prompt, temperature=0.7, json_mode=True)
    data = _extract_json(raw)

    cleaned = []
    for item in data:
        if all(k in item for k in ("text", "option_a", "option_b", "option_c", "option_d", "correct_option")):
            if int(item["correct_option"]) in (0, 1, 2, 3):
                cleaned.append(item)
    if not cleaned:
        raise ValueError("Gemini did not return any valid questions")
    return cleaned


# ---------------------------------------------------------------------------
# 2. Quiz feedback
# ---------------------------------------------------------------------------
def generate_quiz_feedback(quiz_topic: str, score: float, total: int, wrong_questions: list):
    wrong_list_str = "\n".join(f"- {q}" for q in wrong_questions) if wrong_questions else "None — all correct!"
    prompt = f"""A user completed a quiz on "{quiz_topic}" and scored {score}/{total}.

Questions they got WRONG:
{wrong_list_str}

Write a short, encouraging, personalized feedback paragraph (3-5 sentences).
Mention their performance level, any pattern in mistakes, and 1-2 areas to focus on next.
Plain text only, no markdown.
"""
    return _call_gemini(prompt, temperature=0.8, json_mode=False).strip()


# ---------------------------------------------------------------------------
# 3. Resume analysis
# ---------------------------------------------------------------------------
def analyze_resume(resume_text: str, target_role: str = ""):
    role_line = f'The student is targeting the role: "{target_role}".' if target_role else ""
    prompt = f"""You are a career advisor analyzing a student's resume.
{role_line}

Resume text:
---
{resume_text[:8000]}
---

Return ONLY valid JSON, no markdown fences, with this exact structure:
{{
  "summary": "2-3 sentence overview of the candidate",
  "extracted_skills": ["skill1", "skill2", ...],
  "strengths": ["strength1", "strength2", ...],
  "weaknesses": ["weakness1", "weakness2", ...]
}}

Base extracted_skills strictly on what appears in the resume (technical skills, tools, languages).
Strengths and weaknesses should relate to job/career readiness, not grammar.
"""
    raw = _call_gemini(prompt, temperature=0.5, json_mode=True)
    data = _extract_json(raw)

    return {
        "summary": data.get("summary", ""),
        "extracted_skills": data.get("extracted_skills", []),
        "strengths": data.get("strengths", []),
        "weaknesses": data.get("weaknesses", []),
    }


# ---------------------------------------------------------------------------
# 4. Overall readiness report: score + skill gaps + roadmap
# ---------------------------------------------------------------------------
def generate_readiness_report(
    target_role: str,
    profile_skills: list,
    profile_interests: list,
    resume_analysis: dict | None,
    quiz_topic: str | None,
    quiz_score: float | None,
    quiz_total: int | None,
):
    resume_block = "No resume uploaded yet." if not resume_analysis else json.dumps(resume_analysis, indent=2)
    quiz_block = (
        "No quiz attempted yet."
        if quiz_score is None
        else f'Quiz topic: "{quiz_topic}", Score: {quiz_score}/{quiz_total}'
    )

    prompt = f"""You are a career readiness analyzer for a student targeting the role: "{target_role or 'Not specified'}".

Student profile skills: {profile_skills or 'None listed'}
Student interests: {profile_interests or 'None listed'}

Resume analysis:
{resume_block}

Quiz result:
{quiz_block}

Based on ALL of the above, return ONLY valid JSON, no markdown fences, with this exact structure:
{{
  "overall_score": 72,
  "profile_score": 60,
  "resume_score": 75,
  "quiz_score": 80,
  "skill_gaps": [
    {{"skill": "Docker", "importance": "high", "note": "Not mentioned in resume, important for this role"}}
  ],
  "roadmap": [
    {{"topic": "Learn Docker basics", "resource_suggestion": "Docker official getting-started guide", "priority": "high"}}
  ],
  "feedback_summary": "2-4 sentence overall encouraging summary of readiness and what to do next"
}}

All *_score fields must be integers from 0 to 100.
overall_score should be a reasonable weighted combination of profile completeness, resume quality/relevance, and quiz performance
(if quiz wasn't attempted, weight resume/profile more heavily and note that in feedback_summary).
Provide 3-6 skill_gaps and 3-6 roadmap items, ordered by priority (high first).
"""
    raw = _call_gemini(prompt, temperature=0.6, json_mode=True)
    data = _extract_json(raw)

    def clamp(v):
        try:
            return max(0, min(100, int(v)))
        except (TypeError, ValueError):
            return 0

    return {
        "overall_score": clamp(data.get("overall_score", 0)),
        "profile_score": clamp(data.get("profile_score", 0)),
        "resume_score": clamp(data.get("resume_score", 0)),
        "quiz_score": clamp(data.get("quiz_score", 0)),
        "skill_gaps": data.get("skill_gaps", []),
        "roadmap": data.get("roadmap", []),
        "feedback_summary": data.get("feedback_summary", ""),
    }
