import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { FaMusic, FaEnvelope, FaLock, FaEye, FaEyeSlash } from "react-icons/fa";
import { loginUser } from "../api/auth";
import { API_BASE_URL } from "../api/base";
import "./auth.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Show success message from registration
  const successMessage = location.state?.message;

  // VALIDATION
  const validateForm = () => {
    const newErrors = {};

    if (!email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Invalid email";
    }

    if (!password) {
      newErrors.password = "Password is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Clear field errors when user types
  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    if (errors.email) {
      setErrors({ ...errors, email: "" });
    }
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
    if (errors.password) {
      setErrors({ ...errors, password: "" });
    }
  };

  // CONNECT TO BACKEND
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    try {
      const response = await loginUser({ email, password });

      // Check if login was successful and token is present
      if (response.access_token) {
        // Store token in localStorage
        localStorage.setItem("token", response.access_token);
        
        console.log("✅ Login successful! Redirecting to home...");
        
        // Redirect to home page
        navigate("/");
      } else {
        // Handle error response
        const errorMessage = response.msg || response.error || response.message || "Login failed. Please try again.";
        setErrors({ api: errorMessage });
      }
    } catch (error) {
      console.error("Login Error:", error);

      let errorMessage = "Unable to login. Please try again.";
      
      if (error.message.includes('fetch')) {
        errorMessage = `Cannot connect to the API. Make sure the backend is running and reachable at ${API_BASE_URL}.`;
      } else if (error.message.includes('JSON')) {
        errorMessage = "Invalid response from server. Check backend response format.";
      }

      setErrors({ api: errorMessage });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-background">
        <div className="floating-note note-1">♪</div>
        <div className="floating-note note-2">♫</div>
        <div className="floating-note note-3">♪</div>
        <div className="floating-note note-4">♫</div>
      </div>

      <div className="auth-content">
        <div className="auth-card">
          <div className="auth-header">
            <div className="logo-container">
              <FaMusic className="logo-icon" />
            </div>
            <h1 className="auth-title">Welcome Back</h1>
            <p className="auth-subtitle">Login to continue your music journey</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {/* Success message from registration */}
            {successMessage && (
              <div className="success-message" style={{ 
                backgroundColor: '#10b981', 
                color: 'white', 
                padding: '0.75rem', 
                borderRadius: '0.5rem', 
                marginBottom: '1rem',
                textAlign: 'center'
              }}>
                {successMessage}
              </div>
            )}

            {/* API Error message */}
            {errors.api && (
              <div className="error-text" style={{ 
                marginBottom: '1rem', 
                textAlign: 'center',
                padding: '0.75rem',
                backgroundColor: '#fee',
                borderRadius: '0.5rem'
              }}>
                {errors.api}
              </div>
            )}

            {/* EMAIL */}
            <div className="form-group">
              <label htmlFor="email" className="form-label">Email Address</label>
              <div className="input-wrapper">
                <FaEnvelope className="input-icon" />
                <input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={handleEmailChange}
                  className={`form-input ${errors.email ? "input-error" : ""}`}
                  disabled={isLoading}
                />
              </div>
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            {/* PASSWORD */}
            <div className="form-group">
              <label htmlFor="password" className="form-label">Password</label>
              <div className="input-wrapper">
                <FaLock className="input-icon" />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={password}
                  onChange={handlePasswordChange}
                  className={`form-input ${errors.password ? "input-error" : ""}`}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="toggle-password"
                  disabled={isLoading}
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>

            <div className="form-options">
              <label className="remember-me">
                <input type="checkbox" disabled={isLoading} />
                <span>Remember me</span>
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Forgot password?
              </Link>
            </div>

            <button type="submit" className="submit-button" disabled={isLoading}>
              <span>{isLoading ? "Signing In..." : "Sign In"}</span>
              <div className="button-glow"></div>
            </button>

            <div className="auth-divider">
              <span>or</span>
            </div>

            <div className="social-buttons">
              <button type="button" className="social-button google" disabled={isLoading}>
                <svg viewBox="0 0 24 24" className="social-icon">
                  <path
                    fill="currentColor"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="currentColor"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="currentColor"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                </svg>
                Continue with Google
              </button>
            </div>

            <p className="auth-footer">
              Don't have an account?{" "}
              <Link to="/register" className="auth-link">Sign up</Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
