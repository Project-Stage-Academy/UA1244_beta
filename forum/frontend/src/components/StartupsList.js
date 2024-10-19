import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/startupsList.css'; 

const StartupsList = () => {
  const [startups, setStartups] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/startups/')
      .then(response => {
        setStartups(response.data);
      })
      .catch(error => {
        console.error(error);
      });
  }, []);

  return (
    <div className="container">
      <h2>List of Startups</h2>
      <ul className="list-group">
        {startups.map(startup => (
          <li key={startup.id} className="list-group-item">
            <h3>{startup.name}</h3>
            <p>{startup.description}</p>
            <button className="btn btn-primary">Contact</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StartupsList;