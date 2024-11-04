import React, { useState, useEffect } from 'react';
import api from '../api';
import '../styles/UserSettings.css';

const UserSettings = () => {
  const [userData, setUserData] = useState({});
  const [formData, setFormData] = useState({
    username: '',
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  });
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState({});
  const [isUpdating, setIsUpdating] = useState(false); 
  const token = localStorage.getItem('accessToken');

  useEffect(() => {
    api.get('/api/v1/user/update/', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(response => {
      setUserData(response.data);
      setFormData(response.data);
    })
    .catch(error => console.error("Failed to load user data:", error));
  }, [token]);

  const validatePhone = (phone) => {
    const phoneRegex = /^\+?[1-9]\d{1,14}$/; 
    return phoneRegex.test(phone);
  };

  const checkUsernameAvailability = async (username) => {
    try {
      const response = await api.get(`/api/v1/user/check_username/?username=${username}`);
      return response.data.available;
    } catch (error) {
      console.error("Failed to check username availability:", error);
      return false;
    }
  };

  const handleInputChange = async (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });

    if (name === 'phone') {
      if (!validatePhone(value)) {
        setErrors((prevErrors) => ({
          ...prevErrors,
          phone: "Phone number must be in international format.",
        }));
      } else {
        setErrors((prevErrors) => {
          const { phone, ...rest } = prevErrors;
          return rest;
        });
      }
    }

    if (name === 'username') {
      const isAvailable = await checkUsernameAvailability(value);
      if (!isAvailable) {
        setErrors((prevErrors) => ({
          ...prevErrors,
          username: "This username is already taken.",
        }));
      } else {
        setErrors((prevErrors) => {
          const { username, ...rest } = prevErrors;
          return rest;
        });
      }
    }
  };

  const handleUpdate = (e) => {
    e.preventDefault();
    setIsUpdating(true); 

    api.put('/api/v1/user/update/', formData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(response => {
      setMessage("User information updated successfully.");
      setUserData(response.data);
    })
    .catch(error => setMessage("Failed to update user information."))
    .finally(() => setIsUpdating(false)); 
  };

  return (
    <div className="user-settings">
      <h2>User Settings</h2>
      <div>
        <strong>Email:</strong> {userData.email}
      </div>
      <form onSubmit={handleUpdate}>
        <div>
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            placeholder="Username"
            value={formData.username}
            onChange={handleInputChange}
            required
          />
          {errors.username && <div className="error-message">{errors.username}</div>}
        </div>
        <div>
          <label htmlFor="first_name">First Name</label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            placeholder="First Name"
            value={formData.first_name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="last_name">Last Name</label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            placeholder="Last Name"
            value={formData.last_name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div>
          <label htmlFor="phone">Phone Number</label>
          <input
            type="text"
            id="phone"
            name="phone"
            placeholder="Phone Number"
            value={formData.phone}
            onChange={handleInputChange}
          />
          {errors.phone && <div className="error-message">{errors.phone}</div>}
        </div>
        <button type="submit" disabled={Object.keys(errors).length > 0 || isUpdating}>
          {isUpdating ? 'Updating...' : 'Update Information'}
        </button>
      </form>
      {message && <div className="message">{message}</div>}
    </div>
  );
};

export default UserSettings;