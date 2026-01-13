import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  FiGrid, FiBook, FiUsers, FiFileText, FiBarChart2,
  FiHardDrive, FiLogOut, FiMenu, FiX, FiArrowLeft
} from 'react-icons/fi';
import './Layout.css';

const AdminLayout = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/admin', icon: FiGrid, label: 'Dashboard', exact: true },
    { path: '/admin/courses', icon: FiBook, label: 'Courses' },
    { path: '/admin/students', icon: FiUsers, label: 'Students' },
    { path: '/admin/quizzes', icon: FiFileText, label: 'Quizzes' },
    { path: '/admin/reports', icon: FiBarChart2, label: 'Reports' },
    { path: '/admin/drive', icon: FiHardDrive, label: 'Google Drive' },
  ];

  const isActive = (item) => {
    if (item.exact) {
      return location.pathname === item.path;
    }
    return location.pathname.startsWith(item.path);
  };

  return (
    <div className="layout admin-layout">
      {/* Mobile Header */}
      <header className="mobile-header admin-header">
        <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
        <h1 className="logo">Admin Panel</h1>
        <div className="header-user">
          <img 
            src={user?.profile_picture || '/default-avatar.png'} 
            alt={user?.full_name}
            className="avatar-sm"
          />
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`sidebar admin-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h1 className="logo">Admin Panel</h1>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive(item) ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-section">
          <Link to="/dashboard" className="nav-item back-link">
            <FiArrowLeft className="nav-icon" />
            <span>Back to LMS</span>
          </Link>
        </div>

        <div className="sidebar-footer">
          <div className="user-info">
            <img 
              src={user?.profile_picture || '/default-avatar.png'} 
              alt={user?.full_name}
              className="avatar"
            />
            <div className="user-details">
              <p className="user-name">{user?.full_name}</p>
              <p className="user-role">Administrator</p>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <FiLogOut />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Main Content */}
      <main className="main-content admin-content">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
