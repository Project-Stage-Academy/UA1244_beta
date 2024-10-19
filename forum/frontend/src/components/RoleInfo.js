import React from 'react';
import { useParams } from 'react-router-dom';
import '../styles/roleinfo.css'; 

const RoleInfo = () => {
  const { role } = useParams();

  return (
    <div className="container text-center">
      {role === 'startup' && (
        <>
          <h1>Welcome, Startup!</h1>
          <p>You can create and manage your startup profiles, as well as connect with investors.</p>
        </>
      )}
      {role === 'investor' && (
        <>
          <h1>Welcome, Investor!</h1>
          <p>You can browse startups and contact them for potential partnerships or investments.</p>
        </>
      )}
      {role === 'unassigned' && (
        <>
          <h1>Unassigned User</h1>
          <p>You currently have limited access. Please select a role to fully engage with the platform.</p>
        </>
      )}
    </div>
  );
};

export default RoleInfo;