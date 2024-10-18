import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/selectrole.css'; 

const SelectRole = () => {
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRoleChange = (roleName) => {
    axios.post('http://127.0.0.1:8000/api/v1/change-role/', { role: roleName }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      }
    })
      .then(response => {
        if (roleName === 'investor') {
          navigate('/investor');
        } else if (roleName === 'startup') {
          navigate('/startup');
        } else if (roleName === 'unassigned') {
          navigate('/unassigned');
        }
      })
      .catch(() => {
        setError('Could not change role. Please try again.');
      });
  };

  return (
    <div className="container role-selection-container">
      <h2>Select Your Role</h2>
      {error && <p className="alert alert-danger">{error}</p>}
      <div>
        <button onClick={() => handleRoleChange('investor')} className="btn btn-primary">I am an Investor</button>
        <button onClick={() => handleRoleChange('startup')} className="btn btn-success">I am a Startup</button>
        <button onClick={() => handleRoleChange('unassigned')} className="btn btn-secondary">Unassigned</button>
      </div>
    </div>
  );
};

export default SelectRole;
