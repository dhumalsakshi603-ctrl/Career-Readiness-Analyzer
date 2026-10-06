import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { calculateReadiness, getLatestReadiness } from "../api.js";

function priorityClass(priority) {
  const p = (priority || "").toLowerCase();
  if (p === "high") return "tag priority-high";
  if (p === "medium") return "tag priority-medium";
  return "tag priority-low";
}

export default function Readiness() {
  const location = useLocation();
  const attemptId = location.state?.attemptId;

  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getLatestReadiness()
      .then((res) => setAssessment(res.data.assessment === null ? null : res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleCalculate = async () => {
    setCalculating(true);
    setError("");
    try {
      const res = await calculateReadiness(attemptId);
      setAssessment(res.data);
    } catch (err) {
      setError(
        err?.response?.data?.error || "Failed to calculate readiness score."
      );
    } finally {
      setCalculating(false);
    }
  };

  if (loading) return <div className="container loading">Loading...</div>;

  return (
    <div className="container">
      <h1>Career Readiness Dashboard</h1>
      <p>
        Combines your profile, resume analysis, and quiz results into one
        overall readiness score, skill gaps, and a learning roadmap.
      </p>

      {error && <div className="error-box">{error}</div>}

      <button onClick={handleCalculate} disabled={calculating}>
        {calculating ? "Analyzing with Gemini..." : "Calculate My Readiness"}
      </button>

      {!assessment && !calculating && (
        <p style={{ color: "#888" }}>
          No assessment yet — make sure you've filled your profile and
          (optionally) uploaded a resume or taken a quiz, then click above.
        </p>
      )}

      {assessment && (
        <>
          <div className="big-score">{assessment.overall_score}/100</div>
          <p style={{ textAlign: "center", color: "#666" }}>
            Overall Readiness Score {assessment.target_role && `for ${assessment.target_role}`}
          </p>

          <div className="score-grid">
            <div className="score-item">
              <div className="value">{assessment.profile_score}</div>
              <div className="label">Profile</div>
            </div>
            <div className="score-item">
              <div className="value">{assessment.resume_score}</div>
              <div className="label">Resume</div>
            </div>
            <div className="score-item">
              <div className="value">{assessment.quiz_score}</div>
              <div className="label">Quiz</div>
            </div>
          </div>

          <div className="feedback-box">{assessment.feedback_summary}</div>

          <h2>Skill Gaps</h2>
          {assessment.skill_gaps.map((gap, i) => (
            <div className="card" key={i}>
              <strong>{gap.skill}</strong>{" "}
              <span className={priorityClass(gap.importance)}>
                {gap.importance}
              </span>
              <p style={{ marginBottom: 0 }}>{gap.note}</p>
            </div>
          ))}

          <h2>Learning Roadmap</h2>
          {assessment.roadmap.map((item, i) => (
            <div className="card" key={i}>
              <strong>{item.topic}</strong>{" "}
              <span className={priorityClass(item.priority)}>
                {item.priority}
              </span>
              <p style={{ marginBottom: 0 }}>{item.resource_suggestion}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
