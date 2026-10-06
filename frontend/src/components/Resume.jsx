import { useEffect, useState } from "react";
import { getLatestResume, uploadResume } from "../api.js";

export default function Resume() {
  const [resume, setResume] = useState(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getLatestResume()
      .then((res) => setResume(res.data.resume === null ? null : res.data))
      .catch(() => setError("Could not load resume status."))
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please choose a .pdf or .docx file.");
      return;
    }
    setError("");
    setUploading(true);
    try {
      const res = await uploadResume(file);
      setResume(res.data);
    } catch (err) {
      setError(
        err?.response?.data?.error || "Failed to upload/analyze resume."
      );
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <div className="container loading">Loading...</div>;

  return (
    <div className="container">
      <h1>Resume Upload &amp; Analysis</h1>
      <p>Upload your resume (PDF or DOCX) — Gemini will analyze it.</p>

      {error && <div className="error-box">{error}</div>}

      <form onSubmit={handleUpload}>
        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <button type="submit" disabled={uploading}>
          {uploading ? "Uploading & analyzing..." : "Upload Resume"}
        </button>
      </form>
      {uploading && (
        <p className="loading">Extracting text and asking Gemini to analyze it...</p>
      )}

      {resume && resume.analysis && (
        <div className="card">
          <h2>Latest Analysis</h2>
          <p>{resume.analysis.summary}</p>

          <h3>Extracted Skills</h3>
          <div>
            {resume.analysis.extracted_skills.map((s, i) => (
              <span className="tag" key={i}>
                {s}
              </span>
            ))}
          </div>

          <h3>Strengths</h3>
          <ul>
            {resume.analysis.strengths.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>

          <h3>Areas to Improve</h3>
          <ul>
            {resume.analysis.weaknesses.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {resume && !resume.analysis && (
        <div className="feedback-box">
          Resume uploaded, but analysis isn't available yet.
        </div>
      )}
    </div>
  );
}
