import React, { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api';
import '../styles/selectrole.css'; 

const SelectRole = () => {
  const { changeRole } = useContext(AuthContext);
  const navigate = useNavigate();
  const [errorMessage, setErrorMessage] = useState('');

  const handleRoleChange = (role) => {
    api.post('/api/v1/change-role/', { role }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      }
    })
    .then(response => {
      changeRole(role);
      navigate(`/`);
    })
    .catch(error => {
      if (error.response && error.response.status === 401) {
        setErrorMessage('Unauthorized: Invalid token or token expired');
      } else {
        setErrorMessage('Error changing role. Please try again.');
      }
    });
  };

  return (
    <div className="role-selection-container">
      <h2>Select Your Role</h2>
      {errorMessage && <p className="error-message">{errorMessage}</p>}
      <button className="btn btn-primary role-btn" onClick={() => handleRoleChange('investor')}>I am an Investor</button>
      <button className="btn btn-success role-btn" onClick={() => handleRoleChange('startup')}>I am a Startup</button>
      <button className="btn btn-secondary role-btn" onClick={() => handleRoleChange('unassigned')}>Unassigned</button>
    </div>
  );
};

export default SelectRole;
