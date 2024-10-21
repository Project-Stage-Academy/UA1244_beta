import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import '../styles/register.css';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [validationError, setValidationError] = useState('');
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
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationErrorMessage = validateInputs();
    if (validationErrorMessage) {
      setValidationError(validationErrorMessage);
      return;
    }

    setLoading(true);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/register/', {
        email: email,
        password: password,
        username: username,
        first_name: firstName,
        last_name: lastName,
        phone: phone,
      });

      console.log('User registered successfully:', response.data);
      navigate('/login');
    } catch (error) {
      if (error.response) {
        const { data } = error.response;
        if (data.email) {
          setError('This email is already in use.');
        } else if (data.username) {
          setError('This username is already taken.');
        } else {
          setError('Registration failed.');
        }
      } else {
        setError('An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      {validationError && <p className="alert alert-danger">{validationError}</p>}
      {error && <p className="alert alert-danger">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="First Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Last Name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
        <input
          type="tel"
          placeholder="Phone (+XXXXXXXXXXX)"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          required
        />
        <div className="password-container">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
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
        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
    </div>
  );
};

export default Register;