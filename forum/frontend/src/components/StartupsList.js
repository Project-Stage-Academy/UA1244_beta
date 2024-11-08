import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/startupsList.css'; 
import { Link } from 'react-router-dom';

const StartupsList = () => {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true); 

  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken'); 

    console.log('Sending request to API with access_token:', accessToken);

    axios.get('http://localhost:8000/startups/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`  
      }
    })
      .then(response => {
        console.log('Response from API:', response.data);  
        setStartups(response.data);
        setLoading(false); 
      })
      .catch(error => {
        console.error('Error fetching startups:', error);  
        setLoading(false);  
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>; 
  }

  return (
    <div className="startups-container">
      <h2 className="startups-title">List of Startups</h2>
      <ul className="startups-list">
        {startups.map(startup => (
          <li key={startup.startup_id} className="startups-item">
            <h3 className="startups-item-title">{startup.company_name}</h3>
            <p className="startups-item-description">{startup.description}</p>
            <Link to={`/startups/${startup.startup_id}`} className="startups-item-button">Contact</Link> 
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StartupsList;


