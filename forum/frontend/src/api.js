import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,  
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(config => {
  const token = Cookies.get('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (email, password) => {
  try {
    const response = await api.post('/api/v1/login/', { email, password }, { withCredentials: true });
    console.log('User logged in successfully:', response.data);
    
    Cookies.set('access_token', response.data.access, { secure: true });
    Cookies.set('refresh_token', response.data.refresh, { secure: true });
    
    return response.data;
  } catch (err) {
    throw err.response.data;
  }
};

export const refreshToken = async (navigate) => {
  try {
    const response = await api.post('/api/token/refresh/', {}, { withCredentials: true });
    
    Cookies.set('access_token', response.data.access, { secure: true });
    return response.data.access;
  } catch (err) {
    navigate('/login');
  }
};

export const fetchWithAuth = async (url, options = {}, navigate) => {
  let token = Cookies.get('access_token');

  if (!token) {
    navigate('/login');
    return;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    ...options.headers,
  };

  return axios({ url, ...options, headers, withCredentials: true });
};

export default api;
