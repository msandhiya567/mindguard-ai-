import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/api";
import MindGuardLogo from "../components/MindGuardLogo";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const res = await api.post("/auth/login", {
        email,
        password,
      });

      localStorage.setItem("token", res.data.access_token);

      navigate("/dashboard");
    } catch (err) {
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(", "));
      } else {
        setError(
          detail || "Login failed. Please check your credentials."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div
          style={{
            textAlign: "center",
            marginBottom: "28px",
          }}
        >
          <MindGuardLogo size={50} />

          <div
            className="brand"
            style={{
              justifyContent: "center",
              marginTop: "12px",
            }}
          >
            MindGuard AI
          </div>
        </div>

        <h1 className="auth-title">
          Welcome back
        </h1>

        <p className="auth-subtitle">
          Take a moment to understand your digital well-being
          and build healthier digital habits.
        </p>

        <form onSubmit={handleSubmit}>

          <div className="field">
            <label htmlFor="email">
              Email address
            </label>

            <input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          <div className="field">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
            />
          </div>

          {error && (
            <p className="error-text">
              {error}
            </p>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
          >
            {loading
              ? "Signing you in..."
              : "Sign in"}
          </button>

        </form>

        <div className="auth-footer">
          <span>
            Don't have an account?{" "}
          </span>

          <Link to="/register">
            Create one
          </Link>
        </div>

        <p
          style={{
            textAlign: "center",
            fontSize: "12px",
            color: "var(--ink-muted)",
            marginTop: "20px",
            marginBottom: 0,
          }}
        >
          Your digital well-being journey starts here.
        </p>

      </div>
    </div>
  );
}

export default Login;
