import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import '../styles/startupItem.css';

const StartupItem = () => {
  const { id } = useParams();
  const [startup, setStartup] = useState({});
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');  
  const [messageSent, setMessageSent] = useState(false);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/startups/${id}/`)
      .then(response => {
        setStartup(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error(error);
        setLoading(false);
      });
  }, [id]);

  const handleMessageSend = () => {
    if (message.trim() === '') {
      alert('Please enter a message before sending.');
      return;
    }

    axios.post('http://localhost:8000/api/startups/message/', {
      startup_id: id,
      content: message,
    }).then(response => {
      alert('Message sent!');
      setMessage('');  
      setMessageSent(true);  
    }).catch(error => {
      console.error(error);
      alert('Error sending message.');
    });
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="startup-item-container">
      <h2>{startup.company_name}</h2>
      <p>{startup.description}</p>
      <p>Funding Stage: {startup.funding_stage}</p>
      <p>Employees: {startup.number_of_employees}</p>
      <p>Location: {startup.location ? `${startup.location.city}, ${startup.location.country}` : 'No location provided'}</p>
      <p>Total Funding: ${startup.total_funding}</p>
      <p>Website: {startup.website ? <a href={startup.website}>{startup.website}</a> : 'No website available'}</p>

      <div className="message-container">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Enter your message here"
          className="form-control"
        />
        <button onClick={handleMessageSend} className="message-button">
          Send Message
        </button>

        {messageSent && <p className="text-success mt-2">Your message was sent successfully!</p>}
      </div>
    </div>
  );
};

export default StartupItem;