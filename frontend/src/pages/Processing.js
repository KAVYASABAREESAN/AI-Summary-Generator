import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { document } from '../services/api';
import { ArrowLeft, Sparkles, Check, ChevronDown, ChevronUp } from 'lucide-react';
import toast from 'react-hot-toast';

const Processing = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const file = location.state?.file;
    const summaryRef = useRef(null);

    // State
    const [prompt, setPrompt] = useState("Provide a comprehensive summary covering the main ideas, key arguments, and important conclusions.");
    const [isProcessing, setIsProcessing] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [processingStatus, setProcessingStatus] = useState('');
    const [uploadComplete, setUploadComplete] = useState(false);
    const [summaryResult, setSummaryResult] = useState(null);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (!file) {
            navigate('/');
        }
    }, [file, navigate]);

    // Auto-scroll effect when summary is generated
    useEffect(() => {
        if (summaryResult && summaryRef.current) {
            setTimeout(() => {
                summaryRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }, [summaryResult]);

    const handleProcessAndGenerate = async () => {
        setIsProcessing(true);
        setSummaryResult(null);
        const processToast = toast.loading('Starting process...');

        try {
            // Step 1: Upload and Process
            setProgress(30);
            setProcessingStatus('Uploading and extracting text...');

            await document.upload(file);

            setProgress(60);
            setProcessingStatus('Text processed and stored.');
            setUploadComplete(true);
            toast.success('File processed successfully', { id: processToast });

            // Step 2: Generate Summary
            setProcessingStatus('Generating summary with AI...');
            setProgress(80);
            setIsGenerating(true);
            const genToast = toast.loading('Generating summary...', { id: processToast });

            const response = await document.generate(prompt);

            setSummaryResult(response.data);
            setProgress(100);
            setProcessingStatus('Done!');
            toast.success('Summary generated!', { id: genToast });

        } catch (err) {
            console.error(err);
            toast.error(err.response?.data?.detail || 'An error occurred', { id: processToast });
        } finally {
            setIsProcessing(false);
            setIsGenerating(false);
        }
    };

    if (!file) return null;

    return (
        <div className="modern-container">
            <button
                className="nav-item"
                onClick={() => navigate('/')}
                style={{ marginBottom: '1.5rem', width: 'fit-content', paddingLeft: 0, color: 'var(--text-light)' }}
            >
                <ArrowLeft size={18} /> Back to Upload
            </button>

            <h2 style={{ fontSize: '2rem', marginBottom: '2rem', fontWeight: 700 }}>Generate Summary</h2>

            <div className="modern-card" style={{ marginBottom: '2rem', borderLeft: '4px solid var(--accent-color)' }}>
                <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', fontWeight: 600 }}>Customize your summary</h3>
                <textarea
                    className="form-input"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    style={{ minHeight: '120px', resize: 'vertical', lineHeight: '1.6' }}
                    placeholder="e.g. Focus on the main characters and their development..."
                />
            </div>

            <div style={{ marginBottom: '2rem' }}>
                <button
                    className="modern-button"
                    onClick={handleProcessAndGenerate}
                    disabled={isProcessing || isGenerating}
                    style={{ padding: '1rem 2rem', fontSize: '1.1rem' }}
                >
                    {(isProcessing || isGenerating) ? (
                        <>
                            <div className="spinner" style={{ border: '2px solid rgba(255,255,255,0.3)', borderTopColor: 'white', borderRadius: '50%', width: '20px', height: '20px', animation: 'spin 1s linear infinite' }}></div>
                            Processing...
                        </>
                    ) : (
                        <>
                            <Sparkles size={20} /> Generate Summary
                        </>
                    )}
                </button>
            </div>

            <style>{`
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            `}</style>

            {(isProcessing || isGenerating || uploadComplete) && (
                <div className="modern-card" style={{ padding: '2rem' }}>
                    <div style={{ marginBottom: '1rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.8rem', fontWeight: 500 }}>
                            <span style={{ color: 'var(--primary-color)' }}>{processingStatus}</span>
                            <span>{progress}%</span>
                        </div>
                        <div className="progress-container">
                            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                        </div>
                    </div>
                </div>
            )}

            {summaryResult && (
                <div ref={summaryRef} style={{ marginTop: '3rem', animation: 'fadeIn 0.8s ease-out' }}>
                    <div style={{
                        padding: '1rem 1.5rem',
                        background: '#dcfce7',
                        color: '#166534',
                        borderRadius: '16px',
                        marginBottom: '2rem',
                        display: 'flex', alignItems: 'center', gap: '0.8rem',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
                        border: '1px solid #bbf7d0'
                    }}>
                        <div style={{ background: '#166534', borderRadius: '50%', padding: '4px', display: 'flex' }}>
                            <Check size={14} color="white" />
                        </div>
                        <span style={{ fontWeight: 600 }}>Summary generated successfully!</span>
                    </div>

                    <h3 style={{ fontSize: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        📋 <span style={{ background: 'var(--gradient-main)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Your Summary</span>
                    </h3>

                    <div className="modern-card" style={{
                        whiteSpace: 'pre-wrap',
                        lineHeight: '1.8',
                        fontSize: '1.05rem',
                        color: '#334155',
                        boxShadow: 'var(--shadow-xl)',
                        border: 'none',
                        padding: '2.5rem'
                    }}>
                        {summaryResult.summary}
                    </div>

                    {summaryResult.results && (
                        <details className="modern-card" style={{ marginTop: '1.5rem', cursor: 'pointer', borderColor: '#e2e8f0' }}>
                            <summary style={{ fontWeight: 600, color: 'var(--text-light)', listStyle: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span style={{ background: '#f1f5f9', padding: '0.5rem 1rem', borderRadius: '8px' }}>View relevant source chunks</span>
                            </summary>
                            <div style={{ marginTop: '1.5rem' }}>
                                {summaryResult.results.map((chunk, i) => (
                                    <div key={i} style={{
                                        padding: '1.5rem',
                                        background: '#f8fafc',
                                        borderRadius: '12px',
                                        marginBottom: '1rem',
                                        border: '1px solid #f1f5f9'
                                    }}>
                                        <div style={{
                                            fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.8rem',
                                            color: 'var(--primary-color)', textTransform: 'uppercase', letterSpacing: '0.05em'
                                        }}>
                                            Source Chunk {i + 1} • Relevance: {(chunk.score * 100).toFixed(1)}%
                                        </div>
                                        <p style={{ fontSize: '0.95rem', color: '#475569', lineHeight: '1.6', fontStyle: 'italic' }}>"{chunk.text}"</p>
                                    </div>
                                ))}
                            </div>
                        </details>
                    )}

                    <div style={{ height: '50px' }}></div> {/* Spacing at bottom */}
                </div>
            )}
        </div>
    );
};

export default Processing;
