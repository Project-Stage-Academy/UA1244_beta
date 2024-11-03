import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
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

  const refreshAuthToken = useCallback(async () => {
    try {
      const response = await api.post('/api/token/refresh/', { 
        refresh: localStorage.getItem('refreshToken') 
      });
      localStorage.setItem('accessToken', response.data.access);
    } catch (error) {
      alert('Сесія завершена. Будь ласка, увійдіть ще раз.');
      logout(); 
    }
  }, []); 

  useEffect(() => {
    const interval = setInterval(() => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        const { exp } = jwtDecode(token);
        const timeRemaining = exp * 1000 - Date.now();

        if (timeRemaining < 5 * 60 * 1000) { 
          refreshAuthToken();
        } else if (timeRemaining <= 0) {
          logout();
        }
      }
    }, 60000); 
    return () => clearInterval(interval);
  }, [refreshAuthToken]); 

  const login = async (token) => {
    localStorage.setItem('accessToken', token);
    setIsAuthenticated(true);
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