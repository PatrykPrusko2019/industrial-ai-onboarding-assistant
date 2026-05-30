import { useEffect, useState } from "react";
import {
  getCurrentUser,
  loginUser,
  registerUser,
} from "./api/authApi";
import type { User } from "./types/auth";
import "./App.css";

type ViewMode = "login" | "register";

function App() {
  const [viewMode, setViewMode] = useState<ViewMode>("login");
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token")
  );
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadUser() {
      if (!token) {
        return;
      }

      try {
        const currentUser = await getCurrentUser(token);
        setUser(currentUser);
      } catch {
        localStorage.removeItem("access_token");
        setToken(null);
        setUser(null);
      }
    }

    loadUser();
  }, [token]);

  async function handleLogin(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const response = await loginUser({
        email,
        password,
      });

      localStorage.setItem("access_token", response.access_token);
      setToken(response.access_token);
      setUser(response.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRegister(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await registerUser({
        email,
        full_name: fullName,
        password,
      });

      const response = await loginUser({
        email,
        password,
      });

      localStorage.setItem("access_token", response.access_token);
      setToken(response.access_token);
      setUser(response.user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setIsLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
    setViewMode("login");
  }

  if (user) {
    return (
      <main className="app-shell">
        <section className="dashboard-card">
          <div className="dashboard-header">
            <div>
              <p className="eyebrow">Industrial AI Onboarding Assistant</p>
              <h1>Welcome, {user.full_name}</h1>
              <p className="subtitle">
                Your AI-powered onboarding workspace for industrial safety,
                quality procedures and technical documentation.
              </p>
            </div>

            <button className="secondary-button" onClick={handleLogout}>
              Logout
            </button>
          </div>

          <div className="user-box">
            <div>
              <span className="label">Email</span>
              <strong>{user.email}</strong>
            </div>

            <div>
              <span className="label">Role</span>
              <strong className={`role role-${user.role}`}>{user.role}</strong>
            </div>

            <div>
              <span className="label">Status</span>
              <strong>{user.is_active ? "Active" : "Inactive"}</strong>
            </div>
          </div>

          <div className="grid">
            <article className="feature-card">
              <h2>AI Knowledge Assistant</h2>
              <p>
                Ask questions about procedures, safety rules, technical
                documentation and onboarding materials.
              </p>
              <button disabled>Coming next</button>
            </article>

            <article className="feature-card">
              <h2>Learning Path</h2>
              <p>
                Personalized onboarding roadmap with topics, documents and
                checkpoints for new engineers.
              </p>
              <button disabled>Coming next</button>
            </article>

            <article className="feature-card">
              <h2>Quiz Generator</h2>
              <p>
                Generate knowledge checks from internal documents and safety
                procedures.
              </p>
              <button disabled>Coming next</button>
            </article>

            <article className="feature-card">
              <h2>Expert Review</h2>
              <p>
                Safety-critical or uncertain AI answers can be escalated to
                experts.
              </p>
              <button disabled>Coming next</button>
            </article>
          </div>

          {(user.role === "expert" || user.role === "admin") && (
            <section className="expert-panel">
              <h2>Expert / Admin Area</h2>
              <p>
                This section will be used for document upload, knowledge base
                validation and review of AI-generated answers.
              </p>
            </section>
          )}
        </section>
      </main>
    );
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <p className="eyebrow">AI Engineering & App Development</p>

        <h1>
          {viewMode === "login"
            ? "Sign in to onboarding workspace"
            : "Create onboarding account"}
        </h1>

        <p className="subtitle">
          Access the AI-powered onboarding assistant for industrial engineers.
        </p>

        <form
          className="auth-form"
          onSubmit={viewMode === "login" ? handleLogin : handleRegister}
        >
          {viewMode === "register" && (
            <label>
              Full name
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                placeholder="Full name"
                required
              />
            </label>
          )}

          <label>
            Email
            <input
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="employee@example.com"
              type="email"
              required
            />
          </label>

          <label>
            Password
            <input
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Minimum 8 characters"
              type="password"
              required
            />
          </label>

          {error && <p className="error-box">{error}</p>}

          <button type="submit" disabled={isLoading}>
            {isLoading
              ? "Please wait..."
              : viewMode === "login"
              ? "Login"
              : "Register"}
          </button>
        </form>

        <button
          className="link-button"
          onClick={() =>
            setViewMode(viewMode === "login" ? "register" : "login")
          }
        >
          {viewMode === "login"
            ? "Need an account? Register"
            : "Already have an account? Login"}
        </button>
      </section>
    </main>
  );
}

export default App;