import axios from 'axios';
import Cookies from 'js-cookie';
import { jwtDecode} from 'jwt-decode';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': Cookies.get('csrftoken'),
  },
});

export const login = async (email, password) => {
  try {
    const response = await api.post('/api/v1/login/', { email, password }, { withCredentials: true });

    const decodedToken = jwtDecode(response.data.access);
    if (decodedToken.exp * 1000 < Date.now()) {
      throw new Error('Access token has expired');
    }

    Cookies.set('access_token', response.data.access);
    Cookies.set('refresh_token', response.data.refresh);

    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);

    return response.data;
  } catch (err) {
    alert('Invalid token or credentials. Please try again.');
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
    alert('Session expired. Please log in again.');
    window.location.href = '/login';
  }
};

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newAccessToken = await refreshToken();
      api.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
      return api(originalRequest);
    }

    return Promise.reject(error);
  }
);

export default api;