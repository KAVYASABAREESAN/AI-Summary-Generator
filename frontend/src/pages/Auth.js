import React, { useState } from 'react';
import { auth } from '../services/api';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Mail, Lock, User, ArrowRight } from 'lucide-react';

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);

    // Login State
    const [loginEmail, setLoginEmail] = useState('');
    const [loginPassword, setLoginPassword] = useState('');

    // Register State
    const [regName, setRegName] = useState('');
    const [regEmail, setRegEmail] = useState('');
    const [regPassword, setRegPassword] = useState('');
    const [regConfirm, setRegConfirm] = useState('');

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        const loadingToast = toast.loading('Signing in...');

        try {
            const response = await auth.login(loginEmail, loginPassword);
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user_email', response.data.email);
            toast.success('Welcome back!', { id: loadingToast });
            setTimeout(() => {
                window.location.href = '/';
            }, 1000);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Login failed', { id: loadingToast });
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();

        if (regPassword !== regConfirm) {
            toast.error('Passwords do not match');
            return;
        }

        setLoading(true);
        const loadingToast = toast.loading('Creating account...');

        try {
            await auth.register(regEmail, regPassword, regName);
            toast.success('Account created! Please sign in.', { id: loadingToast });
            setIsLogin(true);
            setRegEmail('');
            setRegPassword('');
            setRegName('');
            setRegConfirm('');
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Registration failed', { id: loadingToast });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <center>
                    <div style={{ marginBottom: '1.5rem' }}>
                        <div style={{
                            width: '60px', height: '60px',
                            background: 'var(--gradient-main)',
                            borderRadius: '16px',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            color: 'white', fontSize: '24px', boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.4)'
                        }}>
                            📚
                        </div>
                    </div>
                    <h1 className="auth-title">{isLogin ? 'Welcome back' : 'Create account'}</h1>
                    <p className="auth-subtitle">
                        {isLogin ? 'Enter your credentials to access your summaries' : 'Start your journey with BookSum today'}
                    </p>
                </center>

                <div style={{
                    display: 'flex', background: '#f1f5f9', padding: '4px',
                    borderRadius: '12px', marginBottom: '2rem'
                }}>
                    <div
                        style={{
                            flex: 1, textAlign: 'center', padding: '10px',
                            background: isLogin ? 'white' : 'transparent',
                            borderRadius: '10px', fontWeight: 600, cursor: 'pointer',
                            boxShadow: isLogin ? '0 2px 5px rgba(0,0,0,0.05)' : 'none',
                            color: isLogin ? 'var(--primary-color)' : '#64748b',
                            transition: 'all 0.3s ease'
                        }}
                        onClick={() => setIsLogin(true)}
                    >
                        Sign In
                    </div>
                    <div
                        style={{
                            flex: 1, textAlign: 'center', padding: '10px',
                            background: !isLogin ? 'white' : 'transparent',
                            borderRadius: '10px', fontWeight: 600, cursor: 'pointer',
                            boxShadow: !isLogin ? '0 2px 5px rgba(0,0,0,0.05)' : 'none',
                            color: !isLogin ? 'var(--primary-color)' : '#64748b',
                            transition: 'all 0.3s ease'
                        }}
                        onClick={() => setIsLogin(false)}
                    >
                        Sign Up
                    </div>
                </div>

                {isLogin ? (
                    <form onSubmit={handleLogin}>
                        <div className="form-group">
                            <label className="form-label">Email</label>
                            <div style={{ position: 'relative' }}>
                                <Mail size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: '#94a3b8' }} />
                                <input
                                    type="email"
                                    className="form-input"
                                    placeholder="hello@example.com"
                                    value={loginEmail}
                                    onChange={(e) => setLoginEmail(e.target.value)}
                                    style={{ paddingLeft: '44px' }}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: '#94a3b8' }} />
                                <input
                                    type="password"
                                    className="form-input"
                                    placeholder="••••••••"
                                    value={loginPassword}
                                    onChange={(e) => setLoginPassword(e.target.value)}
                                    style={{ paddingLeft: '44px' }}
                                    required
                                />
                            </div>
                        </div>
                        <button type="submit" className="modern-button" disabled={loading}>
                            {loading ? 'Signing in...' : (
                                <>Sign in <ArrowRight size={18} /></>
                            )}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleRegister}>
                        <div className="form-group">
                            <label className="form-label">Full name</label>
                            <div style={{ position: 'relative' }}>
                                <User size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: '#94a3b8' }} />
                                <input
                                    type="text"
                                    className="form-input"
                                    placeholder="John Doe"
                                    value={regName}
                                    onChange={(e) => setRegName(e.target.value)}
                                    style={{ paddingLeft: '44px' }}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Email</label>
                            <div style={{ position: 'relative' }}>
                                <Mail size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: '#94a3b8' }} />
                                <input
                                    type="email"
                                    className="form-input"
                                    placeholder="hello@example.com"
                                    value={regEmail}
                                    onChange={(e) => setRegEmail(e.target.value)}
                                    style={{ paddingLeft: '44px' }}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: '#94a3b8' }} />
                                <input
                                    type="password"
                                    className="form-input"
                                    placeholder="Create a password"
                                    value={regPassword}
                                    onChange={(e) => setRegPassword(e.target.value)}
                                    style={{ paddingLeft: '44px' }}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Confirm password</label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} style={{ position: 'absolute', left: '14px', top: '14px', color: '#94a3b8' }} />
                                <input
                                    type="password"
                                    className="form-input"
                                    placeholder="Confirm your password"
                                    value={regConfirm}
                                    onChange={(e) => setRegConfirm(e.target.value)}
                                    style={{ paddingLeft: '44px' }}
                                    required
                                />
                            </div>
                        </div>
                        <button type="submit" className="modern-button" disabled={loading}>
                            {loading ? 'Creating account...' : 'Create account'}
                        </button>
                    </form>
                )}
            </div>
        </div>
    );
};

export default Auth;
