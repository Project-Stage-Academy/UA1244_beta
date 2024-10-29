import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/styles.css'; 

const BaseLayout = ({ children }) => {
  const { isAuthenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
       <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <div className="container">
          <Link className="navbar-brand" to="/">Our Project</Link>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/">Home</Link>
              </li>
              {isAuthenticated && (
                <>
                  <li className="nav-item">
                    <Link className="nav-link" to="/notifications">Notifications</Link>
                  </li>
                  <li className="nav-item">
                    <Link className="nav-link" to="/select-role">Select Role</Link>
                  </li>
                </>
              )}
            </ul>
            <ul className="navbar-nav">
              {isAuthenticated ? (
                <li className="nav-item">
                  <button className="btn btn-outline-primary me-2" onClick={handleLogout}>Logout</button>
                </li>
              ) : (
                <>
                  <li className="nav-item">
                    <Link className="btn btn-primary me-2" to="/login">Log In</Link>
                  </li>
                  <li className="nav-item">
                    <Link className="btn btn-secondary" to="/register">Register</Link>
                  </li>
                </>
              )}
            </ul>
          </div>
        </div>
      </nav>

      <div className="container mt-5">
        {children}
      </div>

      <footer className="bg-light text-center text-lg-start mt-auto py-3">
        <div className="text-center p-3">
          © 2024 Our Project | All rights reserved.
        </div>
      </footer>
    </>
  );
};
export default BaseLayout;
