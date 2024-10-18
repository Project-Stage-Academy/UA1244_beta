import React, { useState, useEffect } from 'react';
import '../styles/sendMessageForm.css';

const SendMessageForm = ({ startupId, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    // Завантажуємо існуючі повідомлення стартапу
    const fetchMessages = async () => {
      const response = await fetch(`/api/startups/${startupId}/messages`);
      const data = await response.json();
      setMessages(data);
    };

    fetchMessages();
  }, [startupId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() === '') return;

    // Надсилаємо повідомлення через API
    const response = await fetch(`/api/startups/${startupId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: newMessage })
    });

    const newMsg = await response.json();
    setMessages([...messages, newMsg]);
    setNewMessage('');
  };

  return (
    <div className="send-message-form">
      <h4>Messages</h4>
      <div className="messages-list">
        {messages.map((msg, index) => (
          <p key={index}>{msg.content}</p>
        ))}
      </div>
      <form onSubmit={handleSendMessage}>
        <div className="form-group">
          <input
            type="text"
            placeholder="Type your message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            className="form-control"
          />
        </div>
        <div className="form-buttons">
          <button type="submit" className="btn btn-primary">Send</button>
          <button type="button" className="btn btn-secondary" onClick={onClose}>Close</button>
        </div>
      </form>
    </div>
  );
};

export default SendMessageForm;