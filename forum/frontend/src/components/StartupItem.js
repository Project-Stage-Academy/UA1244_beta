import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import '../styles/startupItem.css';

const StartupItem = () => {
  const { id } = useParams();
  const [startup, setStartup] = useState({});
  const [industries, setIndustries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [messageSent, setMessageSent] = useState(false);

  useEffect(() => {
    const fetchStartupData = async () => {
      const accessToken = localStorage.getItem('accessToken');
      
      try {
        const headers = {
          Authorization: `Bearer ${accessToken}`
        };

        const startupResponse = axios.get(`http://localhost:8000/startups/${id}/`, { headers });
        const industriesResponse = startupResponse.then(response =>
          axios.post(
            'http://localhost:8000/startups/industries/bulk/',
            { ids: response.data.industries },
            { headers }
          )
        );

        const [startupData, industriesData] = await Promise.all([startupResponse, industriesResponse]);

        setStartup(startupData.data);
        setIndustries(industriesData.data);
      } catch (error) {
        console.error("Error fetching startup details:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStartupData();
  }, [id]);

  const handleMessageSend = async () => {
    if (message.trim() === '') {
      alert('Please enter a message before sending.');
      return;
    }

    const accessToken = localStorage.getItem('accessToken');
    try {
      await axios.post(
        'http://localhost:8000/startups/message/',
        { startup_id: id, content: message },
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      alert('Message sent!');
      setMessage('');
      setMessageSent(true);
    } catch (error) {
      console.error("Error sending message:", error);
      alert('Error sending message.');
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="startup-item-container">
      <h2>{startup.company_name}</h2>
      {startup.company_logo && <img src={startup.company_logo} alt={`${startup.company_name} logo`} />}
      <p>{startup.description}</p>
      <p>Funding Stage: {startup.funding_stage}</p>
      <p>Employees: {startup.number_of_employees}</p>
      <p>Location: {startup.location ? `${startup.location.city}, ${startup.location.country}` : 'No location provided'}</p>
      <p>Total Funding: ${startup.total_funding}</p>
      <p>Required Funding: ${startup.required_funding}</p>
      <p>Website: {startup.website ? <a href={startup.website}>{startup.website}</a> : 'No website available'}</p>
      
      <p>Industries: {industries.length > 0 ? industries.map(industry => industry.name).join(', ') : 'No industries listed'}</p>

      <div className="projects-section">
        <h3>Projects</h3>
        {startup.projects && startup.projects.length > 0 ? (
          <ul>
            {startup.projects.map(project => (
              <li key={project.project_id}>
                <h4>{project.title}</h4>
                <p>{project.description}</p>
                <p>Status: {project.status}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No projects available.</p>
        )}
      </div>

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
