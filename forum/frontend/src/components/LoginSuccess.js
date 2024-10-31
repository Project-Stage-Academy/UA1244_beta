import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const LoginSuccess = () => {
  const navigate = useNavigate();

  const handleGoogleLogin = useCallback(async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      try {
        const response = await axios.post(`${API_URL}/api/token/oauth/`, {
          provider: 'google',
          code: code
        });

        const { access, refresh } = response.data;

        if (access && refresh) {
          localStorage.setItem('accessToken', access);
          localStorage.setItem('refreshToken', refresh);
          navigate('/select-role');
        }
      } catch (error) {
        console.error("Google login failed:", error);
        navigate('/login?error=login_failed');
      }
    } else {
      navigate('/login?error=missing_code');
    }
  }, [navigate]);

  useEffect(() => {
    handleGoogleLogin();
  }, [handleGoogleLogin]);

  return <div>Logging you in...</div>;
};

export default LoginSuccess;
