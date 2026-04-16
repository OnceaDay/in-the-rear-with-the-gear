import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";


export default function LoginPage() {
  const navigate = useNavigate();
  const { login, loading, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState({
    username: "",
    password: "",
  });
  const [errorMessage, setErrorMessage] = useState("");

  if (isAuthenticated) {
    return <Navigate to="/products" replace />;
  }

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setErrorMessage("");

    const result = await login(formData.username, formData.password);

    if (result.success) {
      navigate("/products");
    } else {
      setErrorMessage(result.message);
    }
  };

  return (
    <section className="auth-page">
      <div className="auth-card">
        <h1 className="auth-card__title">Sign In</h1>
        <p className="auth-card__subtitle">
          Access your cart, orders, and gear.
        </p>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-form__group">
            <label htmlFor="username" className="auth-form__label">
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              className="auth-form__input"
              required
            />
          </div>

          <div className="auth-form__group">
            <label htmlFor="password" className="auth-form__label">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className="auth-form__input"
              required
            />
          </div>

          {errorMessage && <p className="auth-form__error">{errorMessage}</p>}

          <button type="submit" disabled={loading} className="auth-form__button">
            {loading ? "Signing in..." : "Login"}
          </button>
        </form>
      </div>
    </section>
  );
}