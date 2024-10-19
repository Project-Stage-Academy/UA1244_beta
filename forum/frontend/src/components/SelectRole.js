import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api';
import '../styles/selectrole.css'; 

const SelectRole = () => {
  const { changeRole } = useContext(AuthContext);
  const navigate = useNavigate();

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
        console.error('Unauthorized: Invalid token or token expired');
      } else {
        console.error('Error changing role:', error);
      }
    });
  };

  return (
    <div className="role-selection-container">
      <h2>Select Your Role</h2>
      <button className="btn btn-primary role-btn" onClick={() => handleRoleChange('investor')}>I am an Investor</button>
      <button className="btn btn-success role-btn" onClick={() => handleRoleChange('startup')}>I am a Startup</button>
      <button className="btn btn-secondary role-btn" onClick={() => handleRoleChange('unassigned')}>Unassigned</button>
    </div>
  );
};

export default SelectRole;
