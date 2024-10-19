import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext'; 
import '../styles/login.css';
import api from '../api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useContext(AuthContext); 

  const handleSubmitForm = (email, password) => {
    api.post('/api/v1/login/', {  
        email: email,
        password: password,
    })
    .then(response => {
      if (response.status !== 200) return;
      login(response.data.access); 
      navigate('/select-role'); 
    })
    .catch(error => {
      const errorMessage = error.response?.data?.non_field_errors || 
                           error.response?.data?.email || 
                           error.response?.data?.password || 
                           'Invalid credentials';
      setError(errorMessage);
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
        <button type="submit" className="btn btn-primary">Login</button>
      </form>
    </div>
  );
};

export default Login;