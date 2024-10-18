import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/home.css'; 

const Home = () => {
  return (
    <div className="jumbotron text-center py-5">
      <h1 className="display-4">Welcome to our Project, TEAM BETA!</h1>
      <p className="lead">We aim to bring you the best project management platform.</p>
      <hr className="my-4" />
      <p>Get started by logging in or registering a new account.</p>

      <Link className="btn btn-primary btn-lg m-2" to="/login" role="button">Log In</Link>
      <Link className="btn btn-secondary btn-lg m-2" to="/register" role="button">Register</Link>
    </div>
  );
}

export default Home;
