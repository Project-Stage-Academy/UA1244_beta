import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const LoginSuccess = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleGoogleLogin = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');

      if (code) {
        try {
          const response = await axios.post('http://127.0.0.1:8000/api/token/oauth/', {
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
    };

    handleGoogleLogin();
  }, [navigate]);

  return <div>Logging you in...</div>;
};

export default LoginSuccess;
