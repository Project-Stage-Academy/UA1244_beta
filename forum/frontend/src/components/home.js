import React, { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import '../styles/home.css'; 

const Home = () => {
  const { isAuthenticated } = useContext(AuthContext);

  return (
    <div className="jumbotron text-center py-5">
      {!isAuthenticated ? (
        <>
          <h1 className="display-4">Welcome to our Project, TEAM BETA!</h1>
          <p className="lead">We aim to bring you the best project management platform.</p>
          <hr className="my-4" />
          <p>Get started by logging in or registering a new account.</p>
          <a className="btn btn-primary btn-lg m-2" href="/login" role="button">Log In</a>
          <a className="btn btn-secondary btn-lg m-2" href="/register" role="button">Register</a>
        </>
      ) : (
        <p>You're already logged in. Feel free to explore the platform.</p>
      )}
    </div>
  );
};

export default Home;