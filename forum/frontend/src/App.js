import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Home from './components/home';
import Login from './components/login';
import Register from './components/register';
import SelectRole from './components/SelectRole';
import BaseLayout from './components/BaseLayout';
import StartupPage from './components/StartupPage';
import InvestorPage from './components/InvestorPage';
import UnassignedPage from './components/UnassignedPage';
import StartupsList from './components/StartupsList';
import SendMessageForm from './components/SendMessageForm';
import StartupItem from './components/StartupItem';

function App() {
  return (
    <AuthProvider>
      <Router>
        <BaseLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/select-role" element={<SelectRole />} />
            <Route path="/startup-page" element={<StartupPage />} />
            <Route path="/investor-page" element={<InvestorPage />} />
            <Route path="/unassigned-page" element={<UnassignedPage />} />
            <Route path="/startuplist" element={<StartupsList />} />
            <Route path="/contact/:startupId" element={<SendMessageForm />} />
            <Route path="/startup/:id" element={<StartupItem />} />
          </Routes>
        </BaseLayout>
      </Router>
    </AuthProvider>
  );
}

export default App;