import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CloudUpload, FileText, ArrowRight } from 'lucide-react';

const Home = () => {
    const [file, setFile] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleProcess = () => {
        if (file) {
            navigate('/processing', { state: { file } });
        }
    };

    return (
        <div className="modern-container">
            <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
                <h2 style={{
                    fontSize: '2.5rem',
                    marginBottom: '1rem',
                    background: 'var(--gradient-main)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: 800
                }}>
                    Transform Books into Insights
                </h2>
                <p style={{ color: 'var(--text-light)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
                    Upload your PDF or TXT file and let our AI generate comprehensive summaries, key takeaways, and character analysis in seconds.
                </p>
            </div>

            <label
                className={`upload-area ${dragActive ? 'drag-active' : ''}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                style={{
                    borderColor: dragActive ? 'var(--primary-color)' : '',
                    background: dragActive ? '#eff6ff' : ''
                }}
            >
                <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.txt"
                    style={{ display: 'none' }}
                />
                <div className="upload-icon-wrapper">
                    <CloudUpload size={48} />
                </div>
                <div className="upload-title" style={{ fontSize: '1.5rem', fontWeight: 600 }}>
                    {file ? file.name : "Click or drag file to upload"}
                </div>
                <div className="upload-subtitle" style={{ color: 'var(--text-light)' }}>
                    {file ?
                        `${(file.size / (1024 * 1024)).toFixed(2)} MB` :
                        "Support for PDF and TXT files"
                    }
                </div>
            </label>

            {file && (
                <div className="modern-card" style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    borderLeft: '4px solid var(--primary-color)',
                    padding: '1.5rem', borderRadius: '12px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <div style={{ padding: '12px', background: '#e0e7ff', borderRadius: '12px', color: 'var(--primary-color)' }}>
                            <FileText size={24} />
                        </div>
                        <div>
                            <div style={{ fontWeight: 600, color: 'var(--text-dark)', fontSize: '1.1rem' }}>{file.name}</div>
                            <div style={{ fontSize: '0.9rem', color: 'var(--text-light)' }}>
                                {(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to process
                            </div>
                        </div>
                    </div>
                    {/* Could add a remove button here */}
                </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'center', marginTop: '3rem' }}>
                <button
                    onClick={handleProcess}
                    className="modern-button"
                    style={{ maxWidth: '300px', padding: '1.2rem', fontSize: '1.1rem', borderRadius: '16px' }}
                    disabled={!file}
                >
                    Process Book <ArrowRight size={20} />
                </button>
            </div>

            <div className="stats-grid" style={{ marginTop: '5rem' }}>
                <div className="stat-item" style={{ textAlign: 'center', padding: '2.5rem' }}>
                    <div className="stat-value" style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Instant</div>
                    <div style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-dark)' }}>AI Summarization</div>
                    <p style={{ color: 'var(--text-light)', fontSize: '0.95rem', lineHeight: '1.6' }}>Get detailed summaries and insights in seconds, not hours.</p>
                </div>
                <div className="stat-item" style={{ textAlign: 'center', padding: '2.5rem' }}>
                    <div className="stat-value" style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Secure</div>
                    <div style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-dark)' }}>Private Processing</div>
                    <p style={{ color: 'var(--text-light)', fontSize: '0.95rem', lineHeight: '1.6' }}>Your files are processed securely and never shared.</p>
                </div>
                <div className="stat-item" style={{ textAlign: 'center', padding: '2.5rem' }}>
                    <div className="stat-value" style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>Smart</div>
                    <div style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-dark)' }}>Context Aware</div>
                    <p style={{ color: 'var(--text-light)', fontSize: '0.95rem', lineHeight: '1.6' }}>Our AI understands context, nuance, and key themes.</p>
                </div>
            </div>
        </div>
    );
};

export default Home;
