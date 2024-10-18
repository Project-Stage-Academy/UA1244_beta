import React, { useState } from 'react';
import SendMessageForm from './SendMessageForm';
import '../styles/startupItem.css';

const StartupItem = ({ startup }) => {
  const [showMessageForm, setShowMessageForm] = useState(false);

  const handleContactClick = () => {
    setShowMessageForm(true);
  };

  const handleCloseForm = () => {
    setShowMessageForm(false);
  };

  return (
    <div className="startup-item">
      <h3>{startup.name}</h3>
      <p>{startup.description}</p>
      <button className="btn btn-primary" onClick={handleContactClick}>Contact</button>

      {showMessageForm && (
        <SendMessageForm startupId={startup.id} onClose={handleCloseForm} />
      )}
    </div>
  );
};

export default StartupItem;