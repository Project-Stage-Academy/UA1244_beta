import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/register.css';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const validateInputs = () => {
    if (!username) return 'Username is required';
    if (!email) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Invalid email format';
    if (!firstName) return 'First name is required';
    if (!lastName) return 'Last name is required';
    if (!phone) return 'Phone number is required';
    if (!/^\+?\d{10,15}$/.test(phone)) return 'Phone number must be in the format +XXXXXXXXXXX';
    if (password.length < 8) return 'Password must be at least 8 characters long';
    if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter';
    if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter';
    if (!/[0-9]/.test(password)) return 'Password must contain at least one number';
    if (!/[!@#$%^&*]/.test(password)) return 'Password must contain at least one special character';
    return null;
  };

  const handleSubmitForm = (username, email, password, firstName, lastName, phone) => {
    setLoading(true);
    setError('');
    setSuccess('');

    const validationError = validateInputs();
    if (validationError) {
      setError(validationError);
      setLoading(false);
      return;
    }

    api.post('/api/v1/register/', {
      username,
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      phone,
    })
    .then(response => {
      if (response.status === 201) {
        setSuccess('Registration successful! Redirecting to login...');
        setTimeout(() => navigate('/login'), 2000); // Redirect after 2 seconds
      }
    })
    .catch(error => {
      const errorMessage = error.response?.data?.non_field_errors ||
                           error.response?.data?.email ||
                           error.response?.data?.password ||
                           'Registration failed. Please try again.';
      setError(errorMessage);
    })
    .finally(() => {
      setLoading(false);
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSubmitForm(username, email, password, firstName, lastName, phone);
  };

  const handleGoogleRegistration = () => {
    const clientID = "442876958174-i2eara8qgmaon227mjd2an0b3egffo48.apps.googleusercontent.com";
    const callBackURI = "http://127.0.0.1:3000/login/success/";
    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=${callBackURI}&prompt=consent&response_type=code&client_id=${clientID}&scope=openid%20email%20profile&access_type=offline`;
  };

  return (
    <div className="register-container form-container">
      <h2>Register</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            placeholder="First Name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            placeholder="Last Name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <input
            type="text"
            placeholder="Phone (+XXXXXXXXXXX)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />
        </div>
        <div className="form-group password-field">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Password (min 8 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <span
            className={`password-toggle ${showPassword ? 'show' : 'hide'}`}
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? '🙈' : '🙉'}
          </span>
        </div>
        <button type="submit" disabled={loading} className="btn btn-primary">
          {loading ? 'Registering...' : 'Register'}
        </button>
        <div className="oauth-buttons">
          <button
            type="button"
            className="btn btn-google"
            onClick={handleGoogleRegistration}
          >
            <i className="fab fa-google"></i> Register with Google
          </button>
        </div>
      </form>
    </div>
  );
};

export default Register;
