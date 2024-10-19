import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/startupsList.css'; 
import { Link } from 'react-router-dom';

const StartupsList = () => {
  const [startups, setStartups] = useState([]);

  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken'); 

    console.log('Sending request to API with access_token:', accessToken);

    axios.get('http://localhost:8000/api/startups/list/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`  
      }
    })
      .then(response => {
        console.log('Response from API:', response.data);  
        setStartups(response.data);
      })
      .catch(error => {
        console.error('Error fetching startups:', error);  
      });
  }, []);

  return (
    <div className="startup-list-container">
      <h2>List of Startups</h2>
      <ul className="list-group">
        {startups.map(startup => (
          <li key={startup.startup_id} className="list-group-item">
            <h3>{startup.company_name}</h3>
            <p>{startup.description}</p>
            <Link to={`/startup/${startup.startup_id}`} className="btn btn-primary">Contact</Link> 
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StartupsList;


