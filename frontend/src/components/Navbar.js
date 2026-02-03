import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="container">
        <h1>Chemical Equipment Parameter Visualizer</h1>
        {user && (
          <div className="nav-links">
            <Link 
              to="/dashboard" 
              className={isActive('/dashboard') ? 'active' : ''}
            >
              Dashboard
            </Link>
            <Link 
              to="/upload" 
              className={isActive('/upload') ? 'active' : ''}
            >
              Upload
            </Link>
            <Link 
              to="/datasets" 
              className={isActive('/datasets') ? 'active' : ''}
            >
              Datasets
            </Link>
            <Link 
              to="/history" 
              className={isActive('/history') ? 'active' : ''}
            >
              History
            </Link>
            <button 
              onClick={logout} 
              className="btn btn-secondary"
              style={{ marginLeft: '20px' }}
            >
              Logout ({user.username})
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;