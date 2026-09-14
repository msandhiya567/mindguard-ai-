import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import MindGuardLogo from "../components/MindGuardLogo";

function Assessment() {
  const [form, setForm] = useState({
    age: "",
    gender: "Male",
    academic_level: "Undergraduate",
    avg_daily_usage_hours: "",
    most_used_platform: "Instagram",
    affects_academic_performance: "No",
    sleep_hours_per_night: "",
    mental_health_score: "",
    relationship_status: "Single",
    conflicts_over_social_media: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");
    setLoading(true);

    try {
      const payload = {
        ...form,
        age: Number(form.age),
        avg_daily_usage_hours: Number(
          form.avg_daily_usage_hours
        ),
        sleep_hours_per_night: Number(
          form.sleep_hours_per_night
        ),
        mental_health_score: Number(
          form.mental_health_score
        ),
        conflicts_over_social_media: Number(
          form.conflicts_over_social_media
        ),
      };

      const createRes = await api.post(
        "/assessments",
        payload
      );

      const assessmentId = createRes.data.id;

      await api.post(
        `/assessments/${assessmentId}/predict`
      );

      navigate(`/results/${assessmentId}`);
    } catch (err) {
      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(
          detail.map((d) => d.msg).join(", ")
        );
      } else {
        setError(
          detail ||
            "Something went wrong. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const requiredFields = [
    form.age,
    form.avg_daily_usage_hours,
    form.sleep_hours_per_night,
    form.mental_health_score,
    form.conflicts_over_social_media,
  ];

  const fieldsCompleted =
    requiredFields.filter(
      (value) => value !== ""
    ).length;

  const progress = Math.round(
    (fieldsCompleted / requiredFields.length) * 100
  );

  return (
    <div className="page-column">

      <div className="assessment-container">

        {/* Top navigation */}
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

          <button
            type="button"
            className="btn-secondary"
            onClick={() => navigate("/dashboard")}
          >
            ← Dashboard
          </button>

        </div>

        {/* Main card */}
        <div className="assessment-card-main">

          {/* Introduction */}
          <div
            style={{
              textAlign: "center",
              marginBottom: "32px",
            }}
          >

            <div
              style={{
                width: "64px",
                height: "64px",
                margin: "0 auto 18px",
                borderRadius: "50%",
                background: "var(--sage-bg)",
                display: "grid",
                placeItems: "center",
              }}
            >
              <span
                style={{
                  fontSize: "27px",
                  color: "var(--teal)",
                }}
              >
                ♥
              </span>
            </div>

            <h1
              style={{
                fontSize: "30px",
                marginBottom: "10px",
              }}
            >
              Let's check in
            </h1>

            <p
              style={{
                color: "var(--ink-soft)",
                maxWidth: "520px",
                margin: "0 auto",
                fontSize: "14px",
              }}
            >
              Take a few minutes to reflect on your
              digital habits, sleep, and overall well-being.
            </p>

          </div>

          {/* Progress */}
          <div className="progress-container">

            <div className="progress-header">
              <span>
                Your progress
              </span>

              <span>
                {progress}%
              </span>
            </div>

            <div className="progress-track">

              <div
                className="progress-fill"
                style={{
                  width: `${progress}%`,
                }}
              />

            </div>

            <p
              style={{
                margin: "8px 0 0",
                fontSize: "12px",
                color: "var(--ink-muted)",
              }}
            >
              {fieldsCompleted === 0
                ? "Let's get started."
                : fieldsCompleted === 5
                ? "You're ready to submit."
                : `${5 - fieldsCompleted} required ${
                    5 - fieldsCompleted === 1
                      ? "field"
                      : "fields"
                  } remaining.`}
            </p>

          </div>

          <form onSubmit={handleSubmit}>

            {/* Section 1 */}
            <div className="form-section-title">
              01 · ABOUT YOU
            </div>

            <div className="field">

              <label htmlFor="age">
                How old are you?
              </label>

              <input
                id="age"
                type="number"
                name="age"
                value={form.age}
                onChange={handleChange}
                required
                min="10"
                max="100"
                placeholder="Enter your age"
              />

            </div>

            <div className="field">

              <label htmlFor="gender">
                Gender
              </label>

              <select
                id="gender"
                name="gender"
                value={form.gender}
                onChange={handleChange}
              >
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>

            </div>

            <div className="field">

              <label htmlFor="academic_level">
                Academic level
              </label>

              <select
                id="academic_level"
                name="academic_level"
                value={form.academic_level}
                onChange={handleChange}
              >
                <option>
                  High School
                </option>

                <option>
                  Undergraduate
                </option>

                <option>
                  Postgraduate
                </option>
              </select>

            </div>

            {/* Section 2 */}
            <div className="form-section-title">
              02 · DIGITAL HABITS
            </div>

            <div className="field">

              <label htmlFor="avg_daily_usage_hours">
                Daily social media usage
              </label>

              <p
                style={{
                  fontSize: "12px",
                  color: "var(--ink-muted)",
                  margin: "-2px 0 8px",
                }}
              >
                Approximately how many hours do you
                spend on social media each day?
              </p>

              <input
                id="avg_daily_usage_hours"
                type="number"
                step="0.1"
                name="avg_daily_usage_hours"
                value={form.avg_daily_usage_hours}
                onChange={handleChange}
                required
                min="0"
                max="24"
                placeholder="Example: 4.5"
              />

            </div>

            <div className="field">

              <label htmlFor="most_used_platform">
                Most-used platform
              </label>

              <select
                id="most_used_platform"
                name="most_used_platform"
                value={form.most_used_platform}
                onChange={handleChange}
              >
                <option>Instagram</option>
                <option>YouTube</option>
                <option>TikTok</option>
                <option>Facebook</option>
                <option>LinkedIn</option>
                <option>Other</option>
              </select>

            </div>

            <div className="field">

              <label htmlFor="affects_academic_performance">
                Does social media affect your academic
                performance?
              </label>

              <select
                id="affects_academic_performance"
                name="affects_academic_performance"
                value={
                  form.affects_academic_performance
                }
                onChange={handleChange}
              >
                <option>No</option>
                <option>Yes</option>
              </select>

            </div>

            {/* Section 3 */}
            <div className="form-section-title">
              03 · YOUR WELL-BEING
            </div>

            <div className="field">

              <label htmlFor="sleep_hours_per_night">
                Sleep per night
              </label>

              <p
                style={{
                  fontSize: "12px",
                  color: "var(--ink-muted)",
                  margin: "-2px 0 8px",
                }}
              >
                How many hours do you usually sleep?
              </p>

              <input
                id="sleep_hours_per_night"
                type="number"
                step="0.1"
                name="sleep_hours_per_night"
                value={form.sleep_hours_per_night}
                onChange={handleChange}
                required
                min="0"
                max="24"
                placeholder="Example: 7.5"
              />

            </div>

            <div className="field">

              <label htmlFor="mental_health_score">
                Current well-being
              </label>

              <p
                style={{
                  fontSize: "12px",
                  color: "var(--ink-muted)",
                  margin: "-2px 0 8px",
                }}
              >
                Rate how you're feeling today.
                <br />
                <strong>0</strong> = very difficult
                &nbsp; • &nbsp;
                <strong>10</strong> = feeling very good
              </p>

              <input
                id="mental_health_score"
                type="number"
                name="mental_health_score"
                value={form.mental_health_score}
                onChange={handleChange}
                required
                min="0"
                max="10"
                placeholder="Enter a number from 0 to 10"
              />

            </div>

            <div className="field">

              <label htmlFor="relationship_status">
                Relationship status
              </label>

              <select
                id="relationship_status"
                name="relationship_status"
                value={form.relationship_status}
                onChange={handleChange}
              >
                <option>Single</option>
                <option>In a relationship</option>
                <option>Married</option>
              </select>

            </div>

            <div className="field">

              <label htmlFor="conflicts_over_social_media">
                Social media-related conflicts
              </label>

              <p
                style={{
                  fontSize: "12px",
                  color: "var(--ink-muted)",
                  margin: "-2px 0 8px",
                }}
              >
                How many times have your social media
                habits caused conflicts recently?
              </p>

              <input
                id="conflicts_over_social_media"
                type="number"
                name="conflicts_over_social_media"
                value={
                  form.conflicts_over_social_media
                }
                onChange={handleChange}
                required
                min="0"
                max="50"
                placeholder="Example: 2"
              />

            </div>

            {/* Privacy note */}
            <div
              style={{
                display: "flex",
                gap: "10px",
                alignItems: "flex-start",
                background: "var(--sage-bg)",
                borderRadius: "var(--radius-md)",
                padding: "14px",
                marginTop: "24px",
                marginBottom: "18px",
              }}
            >

              <span
                style={{
                  fontSize: "16px",
                  lineHeight: 1,
                }}
              >
                ✓
              </span>

              <p
                style={{
                  margin: 0,
                  fontSize: "12px",
                  color: "var(--teal-dark)",
                  lineHeight: "1.6",
                }}
              >
                Your answers are used to understand
                your digital-well-being patterns and
                generate personalized insights.
              </p>

            </div>

            {/* Error */}
            {error && (
              <p className="error-text">
                {error}
              </p>
            )}

            {/* Submit */}
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
              style={{
                marginTop: "8px",
              }}
            >
              {loading
                ? "Analyzing your responses..."
                : "Get My Well-Being Insights →"}
            </button>

          </form>

          <p
            style={{
              textAlign: "center",
              fontSize: "12px",
              color: "var(--ink-muted)",
              marginTop: "18px",
              marginBottom: 0,
              lineHeight: "1.5",
            }}
          >
            There are no right or wrong answers.
            Answer based on your usual routine.
          </p>

        </div>

      </div>

    </div>
  );
}

export default Assessment;