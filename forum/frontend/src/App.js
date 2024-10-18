import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/home';
import Login from './components/login';
import Register from './components/register';
import SelectRole from './components/SelectRole';
import BaseLayout from './components/BaseLayout';


function App() {
  return (
    <Router>
      <BaseLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/select-role" element={<SelectRole />} />
        </Routes>
      </BaseLayout>
    </Router>
  );
}

export default App;