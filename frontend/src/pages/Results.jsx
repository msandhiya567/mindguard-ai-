import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/api";
import MindGuardLogo from "../components/MindGuardLogo";

function Results() {
  const { id } = useParams();

  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const res = await api.get(`/assessments/${id}`);
        setData(res.data);
      } catch (err) {
        setError("Could not load this result.");
      }
    };

    fetchResult();
  }, [id]);

  /* Loading */
  if (!data && !error) {
    return (
      <div className="loading-container">
        <div style={{ textAlign: "center" }}>
          <div
            className="spinner"
            style={{
              margin: "0 auto 14px",
            }}
          />

          <p>
            Preparing your well-being insights...
          </p>
        </div>
      </div>
    );
  }

  /* Error */
  if (error) {
    return (
      <div className="page-center">
        <div className="container-medium">

          <div className="dashboard-card">

            <div
              style={{
                textAlign: "center",
                marginBottom: "20px",
              }}
            >
              <MindGuardLogo size={48} />
            </div>

            <h2>
              Something went wrong
            </h2>

            <p className="error-text">
              {error}
            </p>

            <Link to="/dashboard">
              ← Back to Dashboard
            </Link>

          </div>

        </div>
      </div>
    );
  }

  const prediction = data?.prediction;

  /* Prediction unavailable */
  if (!prediction) {
    return (
      <div className="page-center">
        <div className="container-medium">

          <div className="dashboard-card">

            <div
              style={{
                textAlign: "center",
                marginBottom: "20px",
              }}
            >
              <MindGuardLogo size={48} />
            </div>

            <h2>
              Result not available yet
            </h2>

            <p>
              We don't have a prediction for this
              assessment yet.
            </p>

            <Link to="/dashboard">
              ← Back to Dashboard
            </Link>

          </div>

        </div>
      </div>
    );
  }

  const riskLevel = prediction.risk_level;

  const normalizedRisk =
    riskLevel === "Medium" ||
    riskLevel === "Moderate"
      ? "moderate"
      : riskLevel.toLowerCase();

  const riskClass =
    normalizedRisk === "low"
      ? "low"
      : normalizedRisk === "moderate"
      ? "moderate"
      : "high";

  const riskDescription =
    riskClass === "low"
      ? "Your current patterns suggest a relatively healthy relationship with social media. Keep building on the habits that are working for you."
      : riskClass === "moderate"
      ? "Some of your digital habits may be affecting your daily well-being. Small and consistent changes can make a meaningful difference."
      : "Your current patterns suggest that social media may be having a stronger impact on your daily well-being. Consider making gradual, supportive changes.";

  const riskColor =
    riskClass === "low"
      ? "var(--sage)"
      : riskClass === "moderate"
      ? "var(--amber)"
      : "var(--clay)";

  return (
    <div className="page-column">

      <div className="results-container">

        {/* Header */}
        <div className="app-header">

          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
            }}
          >
            <MindGuardLogo size={38} />

            <div>
              <div
                style={{
                  fontFamily: "var(--font-display)",
                  fontSize: "21px",
                  fontWeight: 600,
                }}
              >
                MindGuard AI
              </div>

              <p
                style={{
                  margin: "2px 0 0",
                  fontSize: "12px",
                  color: "var(--ink-muted)",
                }}
              >
                Digital Well-Being
              </p>
            </div>
          </div>

          <Link
            to="/dashboard"
            className="btn-secondary"
          >
            ← Dashboard
          </Link>

        </div>

        {/* Page introduction */}
        <div
          style={{
            textAlign: "center",
            marginBottom: "26px",
          }}
        >

          <div
            style={{
              fontSize: "12px",
              color: "var(--teal)",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0.8px",
              marginBottom: "8px",
            }}
          >
            Your personalized insight
          </div>

          <h1
            style={{
              fontSize: "32px",
              marginBottom: "8px",
            }}
          >
            Here's what we found
          </h1>

          <p
            style={{
              margin: 0,
              color: "var(--ink-soft)",
              fontSize: "14px",
            }}
          >
            Your result is based on the information
            you provided in your assessment.
          </p>

        </div>

        {/* Main result */}
        <div
          className="result-hero"
          style={{
            "--result-glow":
              riskClass === "low"
                ? "var(--sage-bg)"
                : riskClass === "moderate"
                ? "var(--amber-bg)"
                : "var(--clay-bg)",
          }}
        >

          <div
            style={{
              position: "relative",
              zIndex: 1,
            }}
          >

            <div
              style={{
                width: "96px",
                height: "96px",
                margin: "0 auto 18px",
                borderRadius: "50%",
                background:
                  riskClass === "low"
                    ? "var(--sage-bg)"
                    : riskClass === "moderate"
                    ? "var(--amber-bg)"
                    : "var(--clay-bg)",
                display: "grid",
                placeItems: "center",
                border: `4px solid ${riskColor}`,
              }}
            >
              <span
                style={{
                  fontSize: "32px",
                  color: riskColor,
                }}
              >
                {riskClass === "low"
                  ? "✓"
                  : riskClass === "moderate"
                  ? "!"
                  : "•"}
              </span>
            </div>

            <span
              className={`risk-pill ${riskClass}`}
              style={{
                fontSize: "13px",
                marginBottom: "14px",
              }}
            >
              Digital well-being level
            </span>

            <h1 className="result-risk-label">
              {riskLevel} Risk
            </h1>

            <p className="result-confidence">
              {(
                prediction.confidence * 100
              ).toFixed(1)}
              % model confidence
            </p>

            <p
              style={{
                maxWidth: "500px",
                margin: "20px auto 0",
                color: "var(--ink-soft)",
                fontSize: "14px",
                lineHeight: "1.7",
              }}
            >
              {riskDescription}
            </p>

          </div>

        </div>

        {/* Disclaimer */}
        <div
          style={{
            display: "flex",
            gap: "10px",
            alignItems: "flex-start",
            background: "var(--teal-light)",
            borderRadius: "var(--radius-md)",
            padding: "15px 17px",
            marginBottom: "24px",
            color: "var(--teal-dark)",
            fontSize: "13px",
            lineHeight: "1.6",
          }}
        >

          <span
            style={{
              fontWeight: 700,
              fontSize: "16px",
            }}
          >
            i
          </span>

          <div>
            <strong>
              This is a wellness insight.
            </strong>

            <br />

            MindGuard AI provides an AI-based
            digital-well-being assessment. It is not
            a medical diagnosis.
          </div>

        </div>

        {/* Probability */}
        <div
          className="dashboard-card"
          style={{
            marginBottom: "24px",
          }}
        >

          <div className="section-heading">

            <h2>
              Your risk breakdown
            </h2>

            <p>
              See how the AI model evaluated each
              possible risk level.
            </p>

          </div>

          {Object.entries(
            prediction.probabilities || {}
          ).map(([level, prob]) => {

            const percentage = prob * 100;

            const lowerLevel =
              level.toLowerCase();

            const levelClass =
              lowerLevel === "medium" ||
              lowerLevel === "moderate"
                ? "moderate"
                : lowerLevel;

            const barColor =
              levelClass === "low"
                ? "var(--sage)"
                : levelClass === "moderate"
                ? "var(--amber)"
                : "var(--clay)";

            return (
              <div
                className="prob-row"
                key={level}
              >

                <div className="prob-row-top">

                  <span
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      fontWeight: 600,
                      color: "var(--ink)",
                    }}
                  >

                    <span
                      style={{
                        width: "8px",
                        height: "8px",
                        borderRadius: "50%",
                        background: barColor,
                        display: "inline-block",
                      }}
                    />

                    {level}

                  </span>

                  <span>
                    {percentage.toFixed(1)}%
                  </span>

                </div>

                <div className="prob-track">

                  <div
                    className="prob-fill"
                    style={{
                      width: `${percentage}%`,
                      background: barColor,
                    }}
                  />

                </div>

              </div>
            );
          })}

        </div>

        {/* Assessment factors */}
        <div
          className="section-heading"
          style={{
            marginTop: "30px",
          }}
        >

          <h2>
            Your assessment snapshot
          </h2>

          <p>
            Some of the factors included in your
            digital-well-being analysis.
          </p>

        </div>

        <div className="detail-grid">

          <div className="detail-item">

            <div className="label">
              Daily social media usage
            </div>

            <div className="value">
              {data.answer.avg_daily_usage_hours}
              {" "}hrs
            </div>

          </div>

          <div className="detail-item">

            <div className="label">
              Sleep per night
            </div>

            <div className="value">
              {data.answer.sleep_hours_per_night}
              {" "}hrs
            </div>

          </div>

          <div className="detail-item">

            <div className="label">
              Well-being score
            </div>

            <div className="value">
              {data.answer.mental_health_score}/10
            </div>

          </div>

          <div className="detail-item">

            <div className="label">
              Social media conflicts
            </div>

            <div className="value">
              {data.answer.conflicts_over_social_media}
            </div>

          </div>

        </div>

        {/* Recommendations */}
        <div
          className="dashboard-card"
          style={{
            marginTop: "24px",
          }}
        >

          <div className="section-heading">

            <h2>
              Your next small steps
            </h2>

            <p>
              Practical suggestions based on your
              assessment.
            </p>

          </div>

          {prediction.recommendations &&
          prediction.recommendations.length > 0 ? (

            prediction.recommendations.map(
              (rec, index) => (

                <div
                  className="recommendation-item"
                  key={index}
                >

                  <span className="category">
                    {rec.category}
                  </span>

                  <p>
                    {rec.text}
                  </p>

                </div>

              )
            )

          ) : (

            <div className="empty-state">
              No recommendations are available yet.
            </div>

          )}

        </div>

        {/* Positive reminder */}
        <div
          style={{
            marginTop: "24px",
            padding: "22px",
            borderRadius: "var(--radius-lg)",
            background: "var(--sage-bg)",
            textAlign: "center",
          }}
        >

          <div
            style={{
              fontSize: "24px",
              color: "var(--teal)",
              marginBottom: "8px",
            }}
          >
            ♥
          </div>

          <h3
            style={{
              fontSize: "20px",
              marginBottom: "6px",
            }}
          >
            Progress starts with awareness.
          </h3>

          <p
            style={{
              margin: 0,
              color: "var(--ink-soft)",
              fontSize: "13px",
              lineHeight: "1.6",
            }}
          >
            You don't need to change everything at once.
            Focus on one small, realistic improvement.
          </p>

        </div>

        {/* Actions */}
        <div
          style={{
            display: "flex",
            gap: "12px",
            justifyContent: "center",
            marginTop: "28px",
            flexWrap: "wrap",
          }}
        >

          <Link
            to="/assessment"
            className="btn-secondary"
          >
            Take another assessment
          </Link>

          <Link
            to="/dashboard"
            className="btn-primary"
            style={{
              width: "auto",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            Back to Dashboard
          </Link>

        </div>

        {/* Footer */}
        <p
          style={{
            textAlign: "center",
            color: "var(--ink-muted)",
            fontSize: "12px",
            marginTop: "30px",
          }}
        >
          MindGuard AI · Focus on progress,
          not perfection.
        </p>

      </div>

    </div>
  );
}

export default Results;