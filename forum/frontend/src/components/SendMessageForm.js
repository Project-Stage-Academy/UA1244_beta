import React, { useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';

const SendMessageForm = () => {
  const [message, setMessage] = useState('');
  const { startupId } = useParams();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    axios.post('/api/startups/message/', {
      startup_id: startupId,
      content: message,
    })
    .then(() => {
      alert('Message sent successfully!');
      navigate('/startups'); 
    })
    .catch((error) => {
      console.error("Error sending message:", error);
    });
  };

  return (
    <div>
      <h2>Send Message</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message here"
          required
        />
        <button type="submit" className="btn btn-primary">Send</button>
      </form>
    </div>
  );
};

export default SendMessageForm;