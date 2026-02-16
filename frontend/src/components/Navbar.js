import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Book, History, TrendingUp, Settings, LogOut, User } from 'lucide-react';
import { auth } from '../services/api';

const Navbar = () => {
    const location = useLocation();
    const userEmail = localStorage.getItem('user_email');
    const displayUser = userEmail ? userEmail.split('@')[0] : 'User';

    const handleLogout = async () => {
        try {
            await auth.logout();
        } catch (e) {
            console.error(e);
        }
        localStorage.removeItem('token');
        localStorage.removeItem('user_email');
        window.location.href = '/login';
    };

    const isActive = (path) => location.pathname === path ? 'active' : '';

    return (
        <header className="modern-header">
            <Link to="/" className="logo">
                <Book size={24} /> BookSum
            </Link>

            <div className="nav-links">
                <Link to="/" className={`nav-item ${isActive('/')}`}>
                    <Book size={18} /> Home
                </Link>
                <Link to="/history" className={`nav-item ${isActive('/history')}`}>
                    <History size={18} /> History
                </Link>
                <Link to="/stats" className={`nav-item ${isActive('/stats')}`}>
                    <TrendingUp size={18} /> Stats
                </Link>
                <Link to="/settings" className={`nav-item ${isActive('/settings')}`}>
                    <Settings size={18} /> Settings
                </Link>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                    <User size={18} /> {displayUser}
                </div>
                <button onClick={handleLogout} className="nav-item" style={{ color: '#d32f2f' }}>
                    <LogOut size={18} />
                </button>
            </div>
        </header>
    );
};

export default Navbar;
