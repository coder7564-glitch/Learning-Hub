import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Layouts
import MainLayout from './components/layouts/MainLayout';
import AdminLayout from './components/layouts/AdminLayout';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';

// Student Pages
import Dashboard from './pages/student/Dashboard';
import CourseList from './pages/student/CourseList';
import CourseDetail from './pages/student/CourseDetail';
import VideoPlayer from './pages/student/VideoPlayer';
import MyProgress from './pages/student/MyProgress';
import TakeQuiz from './pages/student/TakeQuiz';
import Certificates from './pages/student/Certificates';
import Profile from './pages/student/Profile';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import ManageCourses from './pages/admin/ManageCourses';
import CourseForm from './pages/admin/CourseForm';
import ManageStudents from './pages/admin/ManageStudents';
import ManageQuizzes from './pages/admin/ManageQuizzes';
import Reports from './pages/admin/Reports';
import DriveManager from './pages/admin/DriveManager';

// Loading component
const LoadingScreen = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh',
    backgroundColor: '#F3F4F6'
  }}>
    <div style={{ textAlign: 'center' }}>
      <div className="spinner" style={{
        width: '40px',
        height: '40px',
        border: '3px solid #E5E7EB',
        borderTop: '3px solid #4F46E5',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        margin: '0 auto 1rem'
      }}></div>
      <p style={{ color: '#6B7280' }}>Loading...</p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  </div>
);

// Protected Route component
const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Public Route component (redirect if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (isAuthenticated) {
    return <Navigate to={isAdmin ? '/admin' : '/dashboard'} replace />;
  }

  return children;
};

function App() {
  const { loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={
        <PublicRoute><Login /></PublicRoute>
      } />
      <Route path="/register" element={
        <PublicRoute><Register /></PublicRoute>
      } />

      {/* Student Routes */}
      <Route path="/" element={
        <ProtectedRoute><MainLayout /></ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="courses" element={<CourseList />} />
        <Route path="courses/:slug" element={<CourseDetail />} />
        <Route path="courses/:slug/video/:videoId" element={<VideoPlayer />} />
        <Route path="courses/:slug/quiz/:quizId" element={<TakeQuiz />} />
        <Route path="my-progress" element={<MyProgress />} />
        <Route path="certificates" element={<Certificates />} />
        <Route path="profile" element={<Profile />} />
      </Route>

      {/* Admin Routes */}
      <Route path="/admin" element={
        <ProtectedRoute adminOnly><AdminLayout /></ProtectedRoute>
      }>
        <Route index element={<AdminDashboard />} />
        <Route path="courses" element={<ManageCourses />} />
        <Route path="courses/new" element={<CourseForm />} />
        <Route path="courses/:slug/edit" element={<CourseForm />} />
        <Route path="students" element={<ManageStudents />} />
        <Route path="quizzes" element={<ManageQuizzes />} />
        <Route path="reports" element={<Reports />} />
        <Route path="drive" element={<DriveManager />} />
      </Route>

      {/* 404 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
