import React, { useEffect, useState } from 'react';
import { user } from '../services/api';
import { Link } from 'react-router-dom';
import { Search, Calendar, BookOpen, MessageSquare } from 'lucide-react';
import toast from 'react-hot-toast';

const History = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const response = await user.getHistory();
            setHistory(response.data);
        } catch (e) {
            console.error("Failed to load history", e);
            toast.error("Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    const filteredHistory = history.filter(item =>
        item.title.toLowerCase().includes(search.toLowerCase()) ||
        item.summary.toLowerCase().includes(search.toLowerCase()) ||
        item.prompt.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="modern-container">
            <h2 style={{ fontSize: '2.2rem', marginBottom: '2rem', fontWeight: 700 }}>Your Activities</h2>

            {loading ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                    Loading history...
                </div>
            ) : history.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'white', borderRadius: '24px', boxShadow: 'var(--shadow-lg)' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
                    <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>No summaries yet</h3>
                    <p style={{ color: '#64748b', marginBottom: '2rem' }}>Upload a document to get your first summary!</p>
                    <Link to="/" className="modern-button" style={{ display: 'inline-flex', width: 'auto', textDecoration: 'none', padding: '1rem 2rem' }}>
                        Create New Summary
                    </Link>
                </div>
            ) : (
                <>
                    <div style={{ position: 'relative', marginBottom: '3rem' }}>
                        <Search size={20} style={{ position: 'absolute', left: '20px', top: '18px', color: '#94a3b8' }} />
                        <input
                            type="text"
                            className="form-input"
                            placeholder="Search your summaries..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            style={{ paddingLeft: '50px', fontSize: '1.1rem', borderRadius: '16px' }}
                        />
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                        {filteredHistory.map((item, index) => (
                            <div key={index} className="modern-card" style={{ padding: '2rem', borderLeft: '4px solid var(--primary-color)' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', flexWrap: 'wrap', gap: '1rem' }}>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.8rem' }}>
                                            <span style={{
                                                background: '#e0e7ff', color: 'var(--primary-color)',
                                                padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600
                                            }}>
                                                PDF
                                            </span>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#64748b', fontSize: '0.85rem' }}>
                                                <Calendar size={14} />
                                                {item.timestamp ? new Date(item.timestamp).toLocaleString() : item.date}
                                            </span>
                                        </div>

                                        <h3 style={{ margin: '0 0 1rem 0', fontWeight: '700', fontSize: '1.4rem' }}>{item.title}</h3>

                                        <div style={{ marginBottom: '1.5rem', color: '#334155', lineHeight: '1.6', display: '-webkit-box', WebkitLineClamp: '3', WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                            {item.preview}
                                        </div>

                                        <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.9rem', color: '#64748b' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <BookOpen size={16} /> {item.chunks} chunks
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <MessageSquare size={16} /> {item.prompt.substring(0, 30)}...
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

export default History;
