import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,  
  headers: {
    'Content-Type': 'application/json',
  },
});

export const login = async (email, password) => {
  try {
    const response = await api.post('/api/v1/login/', { email, password }, { withCredentials: true });
    
    Cookies.set('access_token', response.data.access);
    Cookies.set('refresh_token', response.data.refresh);
    
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    
    return response.data;
  } catch (err) {
    throw err.response.data;
  }
};

export const refreshToken = async () => {
  try {
    const refreshToken = Cookies.get('refresh_token') || localStorage.getItem('refresh_token');
    if (!refreshToken) {
      window.location.href = '/login';  
      return;
    }

    const response = await api.post('/api/token/refresh/', { refresh: refreshToken }, { withCredentials: true });
    
    Cookies.set('access_token', response.data.access);
    localStorage.setItem('access_token', response.data.access);

    return response.data.access;
  } catch (err) {
    window.location.href = '/login'; 
  }
};

export default api;