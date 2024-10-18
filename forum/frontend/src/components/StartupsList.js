import React, { useEffect, useState } from 'react';
import StartupItem from './StartupItem';
import '../styles/startupsList.css';

const StartupsList = () => {
  const [startups, setStartups] = useState([]);

  useEffect(() => {
    // Замінити на реальний запит до API для отримання списку стартапів
    const fetchStartups = async () => {
      const response = await fetch('/api/startups');
      const data = await response.json();
      setStartups(data);
    };
    
    fetchStartups();
  }, []);

  return (
    <div className="container">
      <h2>List of Startups</h2>
      <div className="startups-list">
        {startups.map((startup) => (
          <StartupItem key={startup.id} startup={startup} />
        ))}
      </div>
    </div>
  );
};

export default StartupsList;