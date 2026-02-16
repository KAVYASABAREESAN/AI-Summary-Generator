import React, { useState } from 'react';
import { User, Settings as SettingsIcon, Shield, Save, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const Settings = () => {
    const userEmail = localStorage.getItem('user_email');
    const [activeTab, setActiveTab] = useState('profile');

    // Mock state
    const [displayName, setDisplayName] = useState(userEmail ? userEmail.split('@')[0] : '');
    const [summaryType, setSummaryType] = useState('Detailed');
    const [summaryLength, setSummaryLength] = useState(500);
    const [pageNumbers, setPageNumbers] = useState(true);
    const [autoSave, setAutoSave] = useState(true);

    const handleUpdateProfile = () => {
        toast.success("Profile updated successfully!");
    };

    return (
        <div className="modern-container">
            <h2 style={{ fontSize: '2.2rem', marginBottom: '2rem', fontWeight: 700 }}>Settings</h2>

            <div className="tabs" style={{ background: 'white', padding: '6px', borderRadius: '16px', display: 'inline-flex', boxShadow: '0 2px 4px rgba(0,0,0,0.05)', marginBottom: '2rem' }}>
                <div
                    className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setActiveTab('profile')}
                    style={{ borderRadius: '12px', padding: '0.8rem 1.5rem' }}
                >
                    <User size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />
                    Profile
                </div>
                <div
                    className={`tab ${activeTab === 'preferences' ? 'active' : ''}`}
                    onClick={() => setActiveTab('preferences')}
                    style={{ borderRadius: '12px', padding: '0.8rem 1.5rem' }}
                >
                    <SettingsIcon size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />
                    Preferences
                </div>
                <div
                    className={`tab ${activeTab === 'account' ? 'active' : ''}`}
                    onClick={() => setActiveTab('account')}
                    style={{ borderRadius: '12px', padding: '0.8rem 1.5rem' }}
                >
                    <Shield size={18} style={{ marginRight: '8px', verticalAlign: 'text-bottom' }} />
                    Account
                </div>
            </div>

            <div className="modern-card" style={{ maxWidth: '800px' }}>
                {activeTab === 'profile' && (
                    <div className="animate-fade-in">
                        <h3 style={{ marginBottom: '1.5rem' }}>Profile Information</h3>
                        <div className="form-group">
                            <label className="form-label">Display Name</label>
                            <input
                                type="text"
                                className="form-input"
                                value={displayName}
                                onChange={(e) => setDisplayName(e.target.value)}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Email Address</label>
                            <div style={{ position: 'relative' }}>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={userEmail || ''}
                                    disabled
                                    style={{ background: '#f8fafc', color: '#64748b' }}
                                />
                                <CheckCircle size={18} style={{ position: 'absolute', right: '14px', top: '14px', color: '#10b981' }} />
                            </div>
                        </div>
                        <button className="modern-button" onClick={handleUpdateProfile} style={{ width: 'auto', marginTop: '1rem', padding: '0.8rem 2rem' }}>
                            <Save size={18} /> Update Profile
                        </button>
                    </div>
                )}

                {activeTab === 'preferences' && (
                    <div className="animate-fade-in">
                        <h3 style={{ marginBottom: '1.5rem' }}>Generation Preferences</h3>
                        <div className="form-group">
                            <label className="form-label">Default Summary Style</label>
                            <select
                                className="form-input"
                                value={summaryType}
                                onChange={(e) => setSummaryType(e.target.value)}
                            >
                                <option>Detailed Analysis</option>
                                <option>Bullet Points</option>
                                <option>Chapter-wise Breakdown</option>
                                <option>Key Takeaways Only</option>
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Target Length: {summaryLength} words</label>
                            <input
                                type="range"
                                min="100"
                                max="2000"
                                step="100"
                                value={summaryLength}
                                onChange={(e) => setSummaryLength(e.target.value)}
                                style={{ width: '100%', accentColor: 'var(--primary-color)' }}
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                                <span>Short</span>
                                <span>Long</span>
                            </div>
                        </div>
                        <div className="form-group" style={{ display: 'flex', gap: '2rem', marginTop: '2rem' }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={pageNumbers}
                                    onChange={(e) => setPageNumbers(e.target.checked)}
                                    style={{ width: '18px', height: '18px', accentColor: 'var(--primary-color)' }}
                                />
                                Include page numbers
                            </label>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', cursor: 'pointer' }}>
                                <input
                                    type="checkbox"
                                    checked={autoSave}
                                    onChange={(e) => setAutoSave(e.target.checked)}
                                    style={{ width: '18px', height: '18px', accentColor: 'var(--primary-color)' }}
                                />
                                Auto-save summaries
                            </label>
                        </div>
                    </div>
                )}

                {activeTab === 'account' && (
                    <div className="animate-fade-in">
                        <h3 style={{ marginBottom: '1.5rem' }}>Account Management</h3>
                        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                            <button className="modern-button" onClick={() => toast("Feature coming soon!")} style={{ width: 'auto', background: '#f1f5f9', color: '#475569', boxShadow: 'none' }}>
                                Change Password
                            </button>
                            <button className="modern-button" onClick={() => toast("Feature coming soon!")} style={{ width: 'auto', background: '#f1f5f9', color: '#475569', boxShadow: 'none' }}>
                                Export My Data
                            </button>
                            <button
                                className="modern-button"
                                onClick={() => toast.error("Please contact support to delete your account.")}
                                style={{ width: 'auto', background: '#fee2e2', color: '#dc2626', boxShadow: 'none' }}
                            >
                                Delete Account
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Settings;
