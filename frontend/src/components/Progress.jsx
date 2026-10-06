import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { getReadinessHistory } from "../api.js";

export default function Progress() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getReadinessHistory()
      .then((res) => setHistory(res.data))
      .catch(() => setError("Could not load progress history."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container loading">Loading...</div>;

  const chartData = history.map((a, idx) => ({
    name: `#${idx + 1}`,
    date: new Date(a.created_at).toLocaleDateString(),
    overall: a.overall_score,
    profile: a.profile_score,
    resume: a.resume_score,
    quiz: a.quiz_score,
  }));

  return (
    <div className="container">
      <h1>Progress Tracker</h1>
      <p>Your readiness score history over time.</p>

      {error && <div className="error-box">{error}</div>}

      {history.length === 0 && (
        <p style={{ color: "#888" }}>
          No assessments yet. Go to the Readiness tab and calculate your score
          to start tracking progress.
        </p>
      )}

      {history.length > 0 && (
        <>
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="overall" stroke="#4f46e5" strokeWidth={3} name="Overall" />
                <Line type="monotone" dataKey="profile" stroke="#10b981" name="Profile" />
                <Line type="monotone" dataKey="resume" stroke="#f59e0b" name="Resume" />
                <Line type="monotone" dataKey="quiz" stroke="#ef4444" name="Quiz" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <h2>History</h2>
          {history
            .slice()
            .reverse()
            .map((a) => (
              <div className="card" key={a.id}>
                <strong>{new Date(a.created_at).toLocaleString()}</strong>
                <p style={{ marginBottom: 0 }}>
                  Overall: {a.overall_score}/100 · Profile: {a.profile_score} ·
                  {" "}Resume: {a.resume_score} · Quiz: {a.quiz_score}
                </p>
              </div>
            ))}
        </>
      )}
    </div>
  );
}
