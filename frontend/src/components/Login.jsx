import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(username, password);
      navigate("/profile");
    } catch (err) {
      setError(err?.response?.data?.error || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">

        {/* LEFT SIDE */}
        <div className="login-left">
          <div className="brand">
            <div className="brand-icon">🎓</div>
            <span>CareerReady</span>
          </div>

          <div className="welcome-text">
            <h1>Welcome Back!</h1>
            <p>
              Continue your journey toward becoming
              <br />
              career ready.
            </p>
          </div>

          <div className="login-illustration">
            <div className="circle circle-one"></div>
            <div className="circle circle-two"></div>

            <div className="person">
              <div className="head"></div>
              <div className="body"></div>
            </div>

            <div className="laptop">
              <div className="screen">Career</div>
              <div className="keyboard"></div>
            </div>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="login-right">
          <div className="login-content">

            <h2>Sign in</h2>

            <p className="login-subtitle">
              Enter your details to access your account
            </p>

            {error && (
              <div className="login-error">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit}>

              {/* USERNAME */}
              <div className="input-group">
                <label>Username</label>

                <div className="input-wrapper">
                  <span className="input-icon">👤</span>

                  <input
                    type="text"
                    placeholder="Enter your username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* PASSWORD */}
              <div className="input-group">
                <label>Password</label>

                <div className="input-wrapper">
                  <span className="input-icon">🔒</span>

                  <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* OPTIONS */}
              <div className="login-options">
                <label className="remember">
                  <input type="checkbox" />
                  <span>Remember me</span>
                </label>

                <span className="forgot">
                  Forgot password?
                </span>
              </div>

              {/* LOGIN BUTTON */}
              <button
                type="submit"
                className="login-button"
                disabled={loading}
              >
                {loading ? "Signing in..." : "Sign In"}
              </button>

            </form>

            <div className="divider">
              <span>OR</span>
            </div>

            <p className="register-text">
              Don't have an account?{" "}
              <Link to="/register">
                Create an account
              </Link>
            </p>

          </div>
        </div>

      </div>
    </div>
  );
}