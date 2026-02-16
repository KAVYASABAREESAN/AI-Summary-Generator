import React, { useEffect, useState } from 'react';
import { user } from '../services/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Area, AreaChart } from 'recharts';
import { TrendingUp, Book, Layers, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

const Stats = () => {
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsRes, historyRes] = await Promise.all([
                    user.getStats(),
                    user.getHistory()
                ]);
                setStats(statsRes.data);
                setHistory(historyRes.data);
            } catch (e) {
                console.error("Failed to load stats", e);
                toast.error("Failed to load statistics");
            }
        };
        fetchData();
    }, []);

    const totalChunks = history.reduce((acc, item) => acc + (item.chunks || 0), 0);

    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const last7DaysCount = history.filter(item => {
        const date = item.timestamp ? new Date(item.timestamp) : new Date(item.date);
        return date >= sevenDaysAgo;
    }).length;

    // Mock chart data
    const chartData = [
        { name: 'Mon', count: 1 },
        { name: 'Tue', count: 3 },
        { name: 'Wed', count: 2 },
        { name: 'Thu', count: 4 },
        { name: 'Fri', count: 3 },
        { name: 'Sat', count: 5 },
        { name: 'Sun', count: 4 },
    ];

    return (
        <div className="modern-container">
            <h2 style={{ fontSize: '2.2rem', marginBottom: '2rem', fontWeight: 700 }}>Analytics</h2>

            <div className="stats-grid" style={{ marginBottom: '3rem' }}>
                <div className="stat-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.5rem', color: 'var(--text-light)' }}>
                        <Book size={20} /> Books Processed
                    </div>
                    <div className="stat-value">{stats?.books_processed || 0}</div>
                </div>
                <div className="stat-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.5rem', color: 'var(--text-light)' }}>
                        <Layers size={20} /> Total Chunks
                    </div>
                    <div className="stat-value">{totalChunks}</div>
                </div>
                <div className="stat-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.5rem', color: 'var(--text-light)' }}>
                        <Clock size={20} /> Member Since
                    </div>
                    <div className="stat-value" style={{ fontSize: '1.8rem', marginTop: '0.5rem' }}>
                        {stats?.created_at ? new Date(stats.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'N/A'}
                    </div>
                </div>
                <div className="stat-item">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '0.5rem', color: 'var(--text-light)' }}>
                        <TrendingUp size={20} /> Last 7 Days
                    </div>
                    <div className="stat-value">{last7DaysCount}</div>
                </div>
            </div>

            <div className="modern-card" style={{ padding: '2rem', borderRadius: '24px', position: 'relative', overflow: 'hidden' }}>
                <h3 style={{ marginBottom: '2rem', fontSize: '1.4rem' }}>Activity Overview</h3>
                <div style={{ height: '350px', width: '100%' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="var(--primary-color)" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="var(--primary-color)" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8' }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8' }} />
                            <Tooltip
                                contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                                cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '4 4' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="count"
                                stroke="var(--primary-color)"
                                strokeWidth={3}
                                fillOpacity={1}
                                fill="url(#colorCount)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default Stats;
