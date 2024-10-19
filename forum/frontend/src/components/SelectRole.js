import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import axios from 'axios';
import '../styles/selectrole.css'; 

const SelectRole = () => {
  const { changeRole } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleRoleChange = (role) => {
    axios.post('http://localhost:8000/api/v1/change-role/', { role }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      }
    }).then(response => {
      changeRole(role);
      navigate(`/role-info/${role}`);
    }).catch(error => {
      console.error(error);
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