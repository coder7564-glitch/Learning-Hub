import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  FiHome, FiBook, FiBarChart2, FiAward, FiUser, 
  FiLogOut, FiMenu, FiX, FiSettings 
} from 'react-icons/fi';
import './Layout.css';

const MainLayout = () => {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/dashboard', icon: FiHome, label: 'Dashboard' },
    { path: '/courses', icon: FiBook, label: 'Courses' },
    { path: '/my-progress', icon: FiBarChart2, label: 'My Progress' },
    { path: '/certificates', icon: FiAward, label: 'Certificates' },
    { path: '/profile', icon: FiUser, label: 'Profile' },
  ];

  return (
    <div className="layout">
      {/* Mobile Header */}
      <header className="mobile-header">
        <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
        <h1 className="logo">LMS</h1>
        <div className="header-user">
          <img 
            src={user?.profile_picture || '/default-avatar.png'} 
            alt={user?.full_name}
            className="avatar-sm"
          />
        </div>
      </header>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h1 className="logo">LMS</h1>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        {isAdmin && (
          <div className="sidebar-section">
            <p className="sidebar-section-title">Admin</p>
            <Link to="/admin" className="nav-item" onClick={() => setSidebarOpen(false)}>
              <FiSettings className="nav-icon" />
              <span>Admin Panel</span>
            </Link>
          </div>
        )}

        <div className="sidebar-footer">
          <div className="user-info">
            <img 
              src={user?.profile_picture || '/default-avatar.png'} 
              alt={user?.full_name}
              className="avatar"
            />
            <div className="user-details">
              <p className="user-name">{user?.full_name}</p>
              <p className="user-email">{user?.email}</p>
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
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;
