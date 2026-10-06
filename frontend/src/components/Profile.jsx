import { useEffect, useState } from "react";
import { getProfile, updateProfile } from "../api.js";

export default function Profile() {
  const [form, setForm] = useState({
    full_name: "",
    education: "",
    graduation_year: "",
    skills: "",
    interests: "",
    target_role: "",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getProfile()
      .then((res) => {
        setForm({
          full_name: res.data.full_name || "",
          education: res.data.education || "",
          graduation_year: res.data.graduation_year || "",
          skills: res.data.skills || "",
          interests: res.data.interests || "",
          target_role: res.data.target_role || "",
        });
      })
      .catch(() => setError("Could not load profile."))
      .finally(() => setLoading(false));
  }, []);

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    setError("");
    try {
      await updateProfile(form);
      setSaved(true);
    } catch {
      setError("Could not save profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="container loading">Loading profile...</div>;

  return (
    <div className="container">
      <h1>Student Profile</h1>
      <p>Step 1 of your readiness journey — tell us about yourself.</p>

      {error && <div className="error-box">{error}</div>}
      {saved && (
        <div className="feedback-box">Profile saved successfully!</div>
      )}

      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <input value={form.full_name} onChange={handleChange("full_name")} />

        <label>Education (e.g. BCA, B.Tech CSE)</label>
        <input value={form.education} onChange={handleChange("education")} />

        <label>Graduation Year</label>
        <input
          type="number"
          value={form.graduation_year}
          onChange={handleChange("graduation_year")}
        />

        <label>Skills (comma-separated)</label>
        <textarea
          rows="2"
          placeholder="Python, Django, React, SQL"
          value={form.skills}
          onChange={handleChange("skills")}
        />

        <label>Interests (comma-separated)</label>
        <textarea
          rows="2"
          placeholder="Web development, Data science, Cloud computing"
          value={form.interests}
          onChange={handleChange("interests")}
        />

        <label>Target Role</label>
        <input
          placeholder="e.g. Backend Developer, Data Analyst"
          value={form.target_role}
          onChange={handleChange("target_role")}
        />

        <button type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save Profile"}
        </button>
      </form>
    </div>
  );
}
