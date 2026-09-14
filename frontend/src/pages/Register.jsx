import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/api";
import MindGuardLogo from "../components/MindGuardLogo";

function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setSuccess(false);
    setLoading(true);

    try {
      await api.post("/auth/register", {
        full_name: fullName,
        email,
        password,
      });

      setSuccess(true);

      setTimeout(() => {
        navigate("/login");
      }, 1000);
    } catch (err) {
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(detail.map((d) => d.msg).join(", "));
      } else {
        setError(
          detail || "Registration failed. Please try again."
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
          Create your account
        </h1>

        <p className="auth-subtitle">
          Start understanding your digital habits and take
          small steps toward healthier screen time.
        </p>

        <form onSubmit={handleSubmit}>

          <div className="field">
            <label htmlFor="fullName">
              Full name
            </label>

            <input
              id="fullName"
              type="text"
              placeholder="Enter your full name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              autoComplete="name"
            />
          </div>

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
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
          </div>

          {error && (
            <p className="error-text">
              {error}
            </p>
          )}

          {success && (
            <p className="success-text">
              Account created successfully!
              Redirecting to login...
            </p>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading || success}
          >
            {loading
              ? "Creating your account..."
              : success
              ? "Account created ✓"
              : "Create account"}
          </button>

        </form>

        <div className="auth-footer">
          <span>
            Already have an account?{" "}
          </span>

          <Link to="/login">
            Sign in
          </Link>
        </div>

        <p
          style={{
            textAlign: "center",
            fontSize: "12px",
            color: "var(--ink-muted)",
            marginTop: "20px",
            marginBottom: 0,
            lineHeight: "1.5",
          }}
        >
          Your information is used to personalize your
          digital well-being journey.
        </p>

      </div>
    </div>
  );
}

export default Register;