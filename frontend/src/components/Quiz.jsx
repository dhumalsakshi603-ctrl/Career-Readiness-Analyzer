import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { generateQuiz, getQuiz, submitQuiz } from "../api.js";

const OPTION_KEYS = ["option_a", "option_b", "option_c", "option_d"];
const OPTION_LABELS = ["A", "B", "C", "D"];

export default function Quiz() {
  const [stage, setStage] = useState("form"); // form | taking | result
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("medium");
  const [count, setCount] = useState(5);
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!topic.trim()) {
      setError("Please enter a topic.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await generateQuiz(topic, difficulty, count);
      setQuiz(res.data);
      setAnswers({});
      setStage("taking");
    } catch (err) {
      setError(err?.response?.data?.error || "Failed to generate quiz.");
    } finally {
      setLoading(false);
    }
  };

  const selectOption = (questionId, optionIndex) => {
    setAnswers((prev) => ({ ...prev, [questionId]: optionIndex }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await submitQuiz(quiz.id, answers);
      setResult(res.data);
      setStage("result");
    } catch {
      setError("Failed to submit quiz.");
    } finally {
      setLoading(false);
    }
  };

  const goToReadiness = () => {
    navigate("/readiness", { state: { attemptId: result.attempt_id } });
  };

  if (stage === "form") {
    return (
      <div className="container">
        <h1>Skill Assessment Quiz</h1>
        <p>Generate an MCQ quiz on any topic — powered by Gemini.</p>
        {error && <div className="error-box">{error}</div>}
        <form onSubmit={handleGenerate}>
          <label>Topic</label>
          <input
            placeholder="e.g. Python basics, React Hooks, DBMS"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
          <label>Difficulty</label>
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
          <label>Number of Questions</label>
          <input
            type="number"
            min="1"
            max="20"
            value={count}
            onChange={(e) => setCount(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Generating..." : "Generate Quiz"}
          </button>
        </form>
      </div>
    );
  }

  if (stage === "taking") {
    const allAnswered = quiz.questions.length === Object.keys(answers).length;
    return (
      <div className="container">
        <h1>{quiz.title}</h1>
        <p>Topic: {quiz.topic} · Difficulty: {quiz.difficulty}</p>
        {error && <div className="error-box">{error}</div>}
        {quiz.questions.map((q, idx) => (
          <div className="question-card" key={q.id}>
            <p><strong>Q{idx + 1}. {q.text}</strong></p>
            {OPTION_KEYS.map((key, optIdx) => (
              <label
                key={key}
                className={`option-label ${answers[q.id] === optIdx ? "selected" : ""}`}
              >
                <input
                  type="radio"
                  name={`question-${q.id}`}
                  checked={answers[q.id] === optIdx}
                  onChange={() => selectOption(q.id, optIdx)}
                  style={{ width: "auto", marginRight: "8px" }}
                />
                {OPTION_LABELS[optIdx]}. {q[key]}
              </label>
            ))}
          </div>
        ))}
        <button onClick={handleSubmit} disabled={!allAnswered || loading}>
          {loading ? "Submitting..." : "Submit Quiz"}
        </button>
        {!allAnswered && <p style={{ color: "#888" }}>Answer all questions to submit.</p>}
      </div>
    );
  }

  // stage === "result"
  return (
    <div className="container">
      <h1>Quiz Result</h1>
      <p className="score-badge">
        Score: {result.score} / {result.total_questions}
      </p>
      <div className="feedback-box">
  <strong>AI Feedback:</strong>
  <p>{result.ai_feedback}</p>
</div>

<h2>Question Review</h2>

{result.review?.map((q, index) => (
  <div key={q.question_id} className="question-card">
    <p><strong>Q{index + 1}:</strong> {q.text}</p>

    <p>
      Your Answer: {["A", "B", "C", "D"][q.selected_option]}
    </p>

    <p>
      Correct Answer: {["A", "B", "C", "D"][q.correct_option]}
    </p>

    <p>
      {q.is_correct ? "✅ Correct" : "❌ Wrong"}
    </p>
  </div>
))}
      <button onClick={goToReadiness}>
        Calculate My Career Readiness Now
      </button>
      <button className="secondary" onClick={() => setStage("form")}>
        Take Another Quiz
      </button>
    </div>
  );
}
