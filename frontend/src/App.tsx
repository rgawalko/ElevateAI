import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components';
import { Dashboard, Activities, Schedule, ScheduleCreator, Insights, Goals, Chatbot, Login, Typography } from './pages';

// Simple authentication check
const isAuthenticated = () => {
  const token = localStorage.getItem('elevate_auth_token');
  const user = localStorage.getItem('elevate_user');
  return !!(token && user);
};

// Protected Route component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" replace />;
};

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Layout><Dashboard /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/activities" element={
          <ProtectedRoute>
            <Layout><Activities /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/schedule" element={
          <ProtectedRoute>
            <Layout><Schedule /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/schedule/create" element={
          <ProtectedRoute>
            <Layout><ScheduleCreator /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/insights" element={
          <ProtectedRoute>
            <Layout><Insights /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/chatbot" element={
          <ProtectedRoute>
            <Layout><Chatbot /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/goals" element={
          <ProtectedRoute>
            <Layout><Goals /></Layout>
          </ProtectedRoute>
        } />
        <Route path="/typography" element={
          <ProtectedRoute>
            <Layout><Typography /></Layout>
          </ProtectedRoute>
        } />

        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
