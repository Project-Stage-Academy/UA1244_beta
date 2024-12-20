import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/ResetPasswordRequest.css';

const ResetPasswordRequest = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState(''); 

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        setMessage('');
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [message]);

  const validateEmail = (email) => {
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Invalid email format';
    }
    return ''; 
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();

    const validationMessage = validateEmail(email);
    if (validationMessage) {
      setMessage(validationMessage);
      setMessageType('error');
      return;
    }

    try {
      await api.post('/api/custom_reset_password/', { email });
      setMessage("A password reset email has been sent to your email address.");
      setMessageType('success');
    } catch (error) {
      console.error("Error response from server:", error);
      setMessage("Failed to send password reset email. Please try again.");
      setMessageType('error');
    }
  };

  const handleCloseMessage = () => {
    setMessage(''); 
  };

  return (
    <div className="reset-password-request-container">
      <h2 className="reset-password-request-title">Reset Password</h2>
      {message && (
        <div className={`reset-password-request-alert ${messageType}`}>
          {message}
          <button onClick={handleCloseMessage} className="close-button">×</button>
        </div>
      )}
      <form onSubmit={handleResetPassword} className="reset-password-request-form">
        <input
          type="email"
          id="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="reset-password-request-input"
        />
        <button type="submit" className="reset-password-request-button">Send Reset Link</button>
      </form>
    </div>
  );
};

export default ResetPasswordRequest;
