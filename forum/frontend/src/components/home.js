import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import '../styles/home.css'; 

const Home = () => {
  const { isAuthenticated, role } = useContext(AuthContext);

  return (
    <div className="home-container text-center">
      {!isAuthenticated ? (
        <>
          <h1 className="home-heading">Welcome to our Project, TEAM BETA!</h1>
          <p className="home-lead">We aim to bring you the best project management platform.</p>
          <hr className="home-divider" />
          <p className="home-text">Get started by logging in or registering a new account.</p>
          <Link className="home-btn-primary btn-lg m-2" to="/login" role="button">Log In</Link>
          <Link className="home-btn-secondary btn-lg m-2" to="/register" role="button">Register</Link>
        </>
      ) : (
        <>
          {isAuthenticated && role === 'unassigned' && (
            <>
              <p className="home-warning">Your role is unassigned. Please select a role for full access.</p>
              <Link className="home-btn-primary m-2" to="/select-role">Select Role</Link>
              <p className="home-text">
                You have limited functionality, but you can still browse startups.
              </p>
              <Link className="home-btn-secondary m-2" to="/startuplist">View Startups</Link>
            </>
          )}
          {isAuthenticated && role !== 'unassigned' && (
            <div>
              <h1 className="home-heading">Welcome! Your role is {role.charAt(0).toUpperCase() + role.slice(1)}</h1>
              <Link to="/startuplist" className="home-btn-primary m-2">View Startups</Link>
              {role && (
              <Link to={`/${role}-page`} className="home-btn-secondary m-2">
                {role.charAt(0).toUpperCase() + role.slice(1)} Page
              </Link>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Home;
