import React, { Suspense } from 'react'; 
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import BaseLayout from './components/BaseLayout';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './ProtectedRoute';
import LoginSuccess from './components/LoginSuccess';


const Home = React.lazy(() => import('./components/home'));
const Login = React.lazy(() => import('./components/login'));
const Register = React.lazy(() => import('./components/register'));
const SelectRole = React.lazy(() => import('./components/SelectRole'));
const StartupPage = React.lazy(() => import('./components/StartupPage'));
const InvestorPage = React.lazy(() => import('./components/InvestorPage'));
const UnassignedPage = React.lazy(() => import('./components/UnassignedPage'));
const StartupsList = React.lazy(() => import('./components/StartupsList'));
const SendMessageForm = React.lazy(() => import('./components/SendMessageForm'));
const StartupItem = React.lazy(() => import('./components/StartupItem'));
const UserSettings = React.lazy(() => import('./components/UserSettings'));
const ResetPassword = React.lazy(() => import('./components/ResetPassword'));
const ResetPasswordRequest = React.lazy(() => import('./components/ResetPasswordRequest'));


function App() {
  return (
    <AuthProvider>
      <Router>
        <BaseLayout>
          <ErrorBoundary>
            <Suspense fallback={<div>Loading...</div>}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/select-role" element={<SelectRole />} />
                <Route path="/login/success" element={<LoginSuccess />} />
                <Route path="/reset_password_request" element={<ResetPasswordRequest />} />
                <Route path="/reset_password/:uidb64/:token" element={<ResetPassword />} />
               
                <Route path="/startup-page" element={<ProtectedRoute element={StartupPage} />} />
                <Route path="/investor-page" element={<ProtectedRoute element={InvestorPage} />} />
                <Route path="/unassigned-page" element={<ProtectedRoute element={UnassignedPage} />} />
                <Route path="/startuplist" element={<ProtectedRoute element={StartupsList} />} />
                <Route path="/contact/:startupId" element={<ProtectedRoute element={SendMessageForm} />} />
                <Route path="/startups/:id" element={<ProtectedRoute element={StartupItem} />} />
                <Route path="/user-settings" element={<ProtectedRoute element={UserSettings} />} />

              </Routes>
            </Suspense>
          </ErrorBoundary>
        </BaseLayout>
      </Router>
    </AuthProvider>
  );
}

export default App;
