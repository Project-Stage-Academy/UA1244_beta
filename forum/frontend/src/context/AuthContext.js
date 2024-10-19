import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [role, setRole] = useState('unassigned');

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    const storedRole = localStorage.getItem('role');
    setIsAuthenticated(!!token);
    if (storedRole) {
      setRole(storedRole);
    }
  }, []);

  const login = (token, userRole) => {
    localStorage.setItem('accessToken', token);
    localStorage.setItem('role', userRole);
    setIsAuthenticated(true);
    setRole(userRole);
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('role');
    setIsAuthenticated(false);
    setRole('unassigned');
  };

  const changeRole = (newRole) => {
    setRole(newRole);
    localStorage.setItem('role', newRole);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, role, login, logout, changeRole }}>
      {children}
    </AuthContext.Provider>
  );
};