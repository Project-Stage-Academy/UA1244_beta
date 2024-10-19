import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import '../styles/startupdetails.css'; 

const StartupDetails = () => {
  const { id } = useParams();
  const [startup, setStartup] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get(`http://localhost:8000/api/startup/${id}/`)
      .then(response => {
        setStartup(response.data);
      })
      .catch(error => {
        console.error(error);
      });
  }, [id]);

  const handleMessageSend = () => {
    axios.post(`http://localhost:8000/api/startup/${id}/message/`, { message })
      .then(() => {
        alert('Message sent successfully!');
      })
      .catch(error => {
        console.error(error);
      });
  };

  return (
    <div className="container">
      {startup && (
        <>
          <h2>{startup.name}</h2>
          <p>{startup.description}</p>
          <textarea
            className="form-control"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Write a message..."
          />
          <button className="btn btn-primary mt-3" onClick={handleMessageSend}>Send Message</button>
        </>
      )}
    </div>
  );
};

export default StartupDetails;