import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="navbar">
      <div className="links">
        <Link to="/profile">Profile</Link>
        <Link to="/resume">Resume</Link>
        <Link to="/quiz">Quiz</Link>
        <Link to="/readiness">Readiness</Link>
        <Link to="/progress">Progress</Link>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <span style={{ color: "#666" }}>Hi, {user.username}</span>
        <button onClick={handleLogout}>Logout</button>
      </div>
    </div>
  );
}
