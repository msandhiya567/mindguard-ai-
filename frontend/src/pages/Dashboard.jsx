import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../api/api";
import MindGuardLogo from "../components/MindGuardLogo";

function Dashboard() {
  const [assessments, setAssessments] = useState([]);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  useEffect(() => {
    const fetchAssessments = async () => {
      try {
        const res = await api.get("/assessments");
        setAssessments(res.data);
      } catch (err) {
        setError("Could not load your assessments.");
      }
    };

    fetchAssessments();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  const latestAssessment =
    assessments.length > 0 ? assessments[0] : null;

  const latestRisk =
    latestAssessment?.prediction?.risk_level;

  const getRiskClass = (risk) => {
    if (!risk) return "";

    const value = risk.toLowerCase();

    if (value === "medium" || value === "moderate") {
      return "moderate";
    }

    return value;
  };

  const riskClass = getRiskClass(latestRisk);

  return (
    <div className="page-column">

      <div className="dashboard-container">

        {/* Header */}
        <div className="app-header">

          <div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                marginBottom: "12px",
              }}
            >
              <MindGuardLogo size={36} />

              <span
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "22px",
                  fontWeight: 600,
                }}
              >
                MindGuard AI
              </span>
            </div>

            <h2>
              Your Well-Being Dashboard
            </h2>

            <p>
              Understand your digital habits and track
              your progress over time.
            </p>

          </div>

          <button
            onClick={handleLogout}
            className="btn-secondary"
          >
            Sign out
          </button>

        </div>

        {/* Error */}
        {error && (
          <p className="error-text">
            {error}
          </p>
        )}

        {/* Main welcome section */}
        <div
          style={{
            background: "var(--teal)",
            color: "white",
            borderRadius: "var(--radius-xl)",
            padding: "32px",
            marginBottom: "24px",
            position: "relative",
            overflow: "hidden",
          }}
        >

          <div
            style={{
              position: "relative",
              zIndex: 1,
              maxWidth: "600px",
            }}
          >

            <div
              style={{
                fontSize: "12px",
                fontWeight: 700,
                textTransform: "uppercase",
                letterSpacing: "0.8px",
                opacity: 0.8,
                marginBottom: "8px",
              }}
            >
              Your digital well-being
            </div>

            <h1
              style={{
                color: "white",
                fontSize: "30px",
                marginBottom: "10px",
              }}
            >
              Small changes can make
              a meaningful difference.
            </h1>

            <p
              style={{
                color: "rgba(255,255,255,0.82)",
                margin: 0,
                fontSize: "14px",
                lineHeight: "1.7",
              }}
            >
              Understand your patterns, build healthier
              habits, and check your progress over time.
            </p>

            <button
              onClick={() => navigate("/assessment")}
              style={{
                marginTop: "22px",
                padding: "12px 20px",
                border: "none",
                borderRadius: "8px",
                background: "white",
                color: "var(--teal-dark)",
                fontWeight: 700,
                fontSize: "14px",
              }}
            >
              Take a new assessment →
            </button>

          </div>

          <div
            style={{
              position: "absolute",
              width: "230px",
              height: "230px",
              borderRadius: "50%",
              background: "rgba(255,255,255,0.08)",
              right: "-70px",
              top: "-80px",
            }}
          />

        </div>

        {/* Overview */}
        <div className="dashboard-grid">

          {/* Current status */}
          <div className="dashboard-card">

            <div
              style={{
                fontSize: "12px",
                color: "var(--ink-muted)",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                fontWeight: 700,
                marginBottom: "10px",
              }}
            >
              Current status
            </div>

            {latestAssessment?.prediction ? (

              <>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    flexWrap: "wrap",
                  }}
                >
                  <h3>
                    {latestRisk} Risk
                  </h3>

                  <span
                    className={`risk-pill ${riskClass}`}
                  >
                    Latest
                  </span>
                </div>

                <p>
                  Based on your most recent
                  digital-well-being assessment.
                </p>

                <Link
                  to={`/results/${latestAssessment.id}`}
                  style={{
                    fontSize: "14px",
                    fontWeight: 600,
                  }}
                >
                  View your insights →
                </Link>
              </>

            ) : (

              <>
                <h3>
                  No assessment yet
                </h3>

                <p>
                  Take your first check-in to understand
                  your current digital habits.
                </p>
              </>

            )}

          </div>

          {/* Journey */}
          <div className="dashboard-card">

            <div
              style={{
                fontSize: "12px",
                color: "var(--ink-muted)",
                textTransform: "uppercase",
                letterSpacing: "0.5px",
                fontWeight: 700,
                marginBottom: "10px",
              }}
            >
              Your journey
            </div>

            <h3>
              {assessments.length}
            </h3>

            <p>
              {assessments.length === 1
                ? "assessment completed so far."
                : "assessments completed so far."}
            </p>

            <div
              style={{
                marginTop: "14px",
                height: "6px",
                background: "var(--line-light)",
                borderRadius: "100px",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: `${Math.min(
                    assessments.length * 20,
                    100
                  )}%`,
                  height: "100%",
                  background: "var(--teal)",
                  borderRadius: "100px",
                }}
              />
            </div>

          </div>

        </div>

        {/* Assessment history */}
        <div
          style={{
            marginTop: "32px",
          }}
        >

          <div className="section-heading">

            <h2>
              Assessment history
            </h2>

            <p>
              Review your previous digital-well-being
              check-ins.
            </p>

          </div>

          {assessments.length === 0 ? (

            <div className="empty-state">

              <div
                style={{
                  fontSize: "32px",
                  marginBottom: "10px",
                  color: "var(--teal)",
                }}
              >
                ○
              </div>

              <h3
                style={{
                  fontSize: "20px",
                  marginBottom: "6px",
                }}
              >
                Your journey starts here
              </h3>

              <p
                style={{
                  margin: "0 auto 18px",
                  maxWidth: "420px",
                }}
              >
                Complete your first assessment to receive
                personalized digital-well-being insights.
              </p>

              <button
                onClick={() => navigate("/assessment")}
                className="btn-primary"
                style={{
                  width: "auto",
                }}
              >
                Start assessment
              </button>

            </div>

          ) : (

            <div>

              {assessments.map((a) => {

                const risk =
                  a.prediction?.risk_level;

                const currentRiskClass =
                  getRiskClass(risk);

                return (
                  <div
                    className="assessment-card"
                    key={a.id}
                  >

                    <div>

                      <div className="assessment-meta">
                        <strong>
                          Assessment #{a.id}
                        </strong>
                      </div>

                      <div
                        style={{
                          fontSize: "12px",
                          color: "var(--ink-muted)",
                          marginTop: "4px",
                        }}
                      >
                        {new Date(
                          a.submitted_at
                        ).toLocaleString()}
                      </div>

                    </div>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                      }}
                    >

                      <span
                        className={`risk-pill ${
                          currentRiskClass || ""
                        }`}
                      >
                        {risk || "Pending"}
                      </span>

                      <Link
                        to={`/results/${a.id}`}
                        style={{
                          fontSize: "13px",
                          fontWeight: 600,
                        }}
                      >
                        View
                      </Link>

                    </div>

                  </div>
                );
              })}

            </div>

          )}

        </div>

        {/* Bottom button */}
        {assessments.length > 0 && (

          <div
            style={{
              marginTop: "28px",
              padding: "22px",
              borderTop: "1px solid var(--line)",
              textAlign: "center",
            }}
          >

            <p
              style={{
                margin: "0 0 12px",
                color: "var(--ink-soft)",
                fontSize: "14px",
              }}
            >
              Ready to check in again?
            </p>

            <button
              onClick={() => navigate("/assessment")}
              className="btn-secondary"
            >
              Take another assessment
            </button>

          </div>

        )}

        <p
          style={{
            textAlign: "center",
            color: "var(--ink-muted)",
            fontSize: "12px",
            marginTop: "35px",
          }}
        >
          MindGuard AI · Focus on progress, not perfection.
        </p>

      </div>

    </div>
  );
}

export default Dashboard;