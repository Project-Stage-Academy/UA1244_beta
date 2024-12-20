import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import '../styles/ResetPassword.css';

const ResetPassword = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [isSuccessful, setIsSuccessful] = useState(false); 
  const { uidb64, token } = useParams();
  const navigate = useNavigate();

  const validatePassword = (password) => {
    if (password.length < 8) return 'Password must be at least 8 characters long.';
    if (!/[A-Z]/.test(password)) return 'Password must contain at least one uppercase letter.';
    if (!/[a-z]/.test(password)) return 'Password must contain at least one lowercase letter.';
    if (!/[0-9]/.test(password)) return 'Password must contain at least one number.';
    if (!/[!@#$%^&*]/.test(password)) return 'Password must contain at least one special character.';
    return ''; 
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    const validationMessage = validatePassword(password);
    if (validationMessage) {
      setMessage(validationMessage);
      return;
    }
    if (password !== confirmPassword) {
      setMessage("Passwords do not match.");
      return;
    }
    try {
      await api.post(`reset_password_confirm/${uidb64}/${token}/`, { password });
      setMessage("Password has been reset successfully.");
      setIsSuccessful(true); 
    } catch (error) {
      if (error.response && error.response.status === 400) {
        setMessage("Failed to reset password. The link may be invalid or expired.");
      } else {
        setMessage("An error occurred while resetting the password. Please try again.");
      }
    }
  };

  const handleNavigateToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="reset-password-container">
      <h2>Set New Password</h2>
      {message && <div className="alert alert-info">{message}</div>}
      {isSuccessful ? (
        <button onClick={handleNavigateToLogin} className="btn btn-primary">
          Go to Login
        </button>
      ) : (
        <form onSubmit={handleResetPassword}>
          <label>New Password</label>
          <input
            type="password"
            placeholder="New Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="form-group"
          />
          <label>Confirm New Password</label>
          <input
            type="password"
            placeholder="Confirm New Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="form-group"
          />
          <button type="submit" className="btn btn-primary">Reset Password</button>
        </form>
      )}
    </div>
  );
};

export default ResetPassword;

