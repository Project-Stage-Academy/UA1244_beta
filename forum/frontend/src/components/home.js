import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import '../styles/home.css'; 

const Home = () => {
  const { isAuthenticated, role } = useContext(AuthContext);

  return (
    <div className="container text-center">
      {!isAuthenticated ? (
        <>
          <h1 className="display-4">Welcome to our Project, TEAM BETA!</h1>
          <p className="lead">We aim to bring you the best project management platform.</p>
          <hr className="my-4" />
          <p>Get started by logging in or registering a new account.</p>
          <Link className="btn btn-primary btn-lg m-2" to="/login" role="button">Log In</Link>
          <Link className="btn btn-secondary btn-lg m-2" to="/register" role="button">Register</Link>
        </>
      ) : (
        <>
          {role === 'unassigned' && (
            <>
              <h1 className="display-4">Welcome, Unassigned User!</h1>
              <p>You currently have limited access. Please choose a role to fully use the platform.</p>
              <Link className="btn btn-warning btn-lg" to="/select-role">Choose Your Role</Link>
            </>
          )}
          {role === 'startup' && (
            <>
              <h1 className="display-4">Welcome, Startup!</h1>
              <p>Explore and collaborate with investors. View other startups as well.</p>
              <Link className="btn btn-success btn-lg" to="/startups-list">View Startups</Link>
            </>
          )}
          {role === 'investor' && (
            <>
              <h1 className="display-4">Welcome, Investor!</h1>
              <p>Browse startups and contact them for potential investment opportunities.</p>
              <Link className="btn btn-info btn-lg" to="/startups-list">View Startups</Link>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Home;