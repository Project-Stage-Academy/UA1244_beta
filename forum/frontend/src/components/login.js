import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext'; 
import '../styles/login.css';
import api from '../api';

const reachGoogle = () => {
  const clientID = "442876958174-i2eara8qgmaon227mjd2an0b3egffo48.apps.googleusercontent.com";
  const callBackURI = "http://127.0.0.1:3000/login/success/";
  window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?redirect_uri=${callBackURI}&prompt=consent&response_type=code&client_id=${clientID}&scope=openid%20email%20profile&access_type=offline`;
};

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const handleSubmitForm = (email, password) => {
    setLoading(true);
    setError('');
    setSuccess('');

    api.post('/api/v1/login/', {  
      email: email,
      password: password,
    })
    .then(response => {
      if (response.status === 200) {
        login(response.data.access);
        setSuccess('Login successful! Redirecting...');
        setTimeout(() => navigate('/select-role'), 2000); // Redirect after 2 seconds
      }
    })
    .catch(error => {
      const errorMessage = error.response?.data?.non_field_errors || 
                           error.response?.data?.email || 
                           error.response?.data?.password || 
                           'Invalid credentials. Please check your email and password.';
      setError(errorMessage);
    })
    .finally(() => {
      setLoading(false);
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSubmitForm(email, password);
  };

  return (
    <div className="login-container form-container">
      <h2>Login</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="form-group"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="form-group"
        />
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <div className="oauth-buttons">
        <button
          type="button"
          className="btn btn-google"
          onClick={reachGoogle}
        >
          <i className="fab fa-google"></i> Login with Google
        </button>
      </div>
    </div>
  );
};

export default Login;
