import React, { createContext, useState, useEffect, useContext } from 'react';
import { jwtDecode} from 'jwt-decode';
import api from '../api'; 

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [role, setRole] = useState('unassigned');

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      const { exp } = jwtDecode(token); 
      if (exp * 1000 < Date.now()) {
        logout();
      } else {
        setIsAuthenticated(true);
      }
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        const { exp } = jwtDecode(token);
        if (exp * 1000 < Date.now()) {
          
          logout();
        }
      }
    }, 60000); 
    return () => clearInterval(interval);
  }, []);

  const login = async (token) => {
    localStorage.setItem('accessToken', token);
    setIsAuthenticated(true);
  };

  const refreshAuthToken = async () => {
    try {
      const response = await api.post('/api/token/refresh/', { 
        refresh: localStorage.getItem('refreshToken') 
      });
      localStorage.setItem('accessToken', response.data.access);
    } catch (error) {
      logout(); 
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setIsAuthenticated(false);
    setRole('unassigned');
  };

  const changeRole = (newRole) => {
    setRole(newRole);
    localStorage.setItem('role', newRole);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, role, login, logout, changeRole, refreshAuthToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
