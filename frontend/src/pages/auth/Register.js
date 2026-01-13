import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { toast } from 'react-toastify';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  const [loading, setLoading] = useState(false);
  const { register, googleLogin } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const result = await register(formData);
    
    if (result.success) {
      toast.success('Registration successful! Please sign in.');
      navigate('/login');
    } else {
      const errors = result.error;
      if (typeof errors === 'object') {
        Object.values(errors).forEach(err => {
          toast.error(Array.isArray(err) ? err[0] : err);
        });
      } else {
        toast.error(errors);
      }
    }
    
    setLoading(false);
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true);
    const result = await googleLogin(credentialResponse);
    
    if (result.success) {
      toast.success('Welcome!');
      navigate('/dashboard');
    } else {
      toast.error(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1 className="auth-logo">LMS</h1>
          <h2>Create Account</h2>
          <p>Start your learning journey today</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-row">
            <div className="form-group">
              <label className="label">First Name</label>
              <input
                type="text"
                name="first_name"
                className="input"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="First name"
                required
              />
            </div>
            <div className="form-group">
              <label className="label">Last Name</label>
              <input
                type="text"
                name="last_name"
                className="input"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Last name"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="label">Email</label>
            <input
              type="email"
              name="email"
              className="input"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
            />
          </div>

          <div className="form-group">
            <label className="label">Password</label>
            <input
              type="password"
              name="password"
              className="input"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password"
              minLength={8}
              required
            />
          </div>

          <div className="form-group">
            <label className="label">Confirm Password</label>
            <input
              type="password"
              name="password_confirm"
              className="input"
              value={formData.password_confirm}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="auth-divider">
          <span>or continue with</span>
        </div>

        <div className="google-login-wrapper">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => toast.error('Google login failed')}
            theme="outline"
            size="large"
            width="100%"
          />
        </div>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
};

export default Register;
