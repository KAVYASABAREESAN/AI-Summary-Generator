import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add a request interceptor to inject the token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export const auth = {
    login: (email, password) => api.post('/auth/login', { email, password }),
    register: (email, password, name) => api.post('/auth/register', { email, password, name }),
    logout: () => api.post('/auth/logout'),
};

export const document = {
    upload: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/process', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    generate: (prompt) => api.post('/generate', { prompt, email: localStorage.getItem('user_email') || '' }),
    // Backend expects email in body? No, it extracts from token usually, but let's check backend/app.py
    // Backend: `generate_summary(req: GenerateRequest, email: str = Depends(get_current_user_email))`
    // `GenerateRequest` has `email: str` ?
    // Yes: `class GenerateRequest(BaseModel): prompt: str; email: str`
    // So we need to send email in body AND token in header.
};

export const user = {
    getHistory: () => api.get('/history'),
    getStats: () => api.get('/stats'),
};

export default api;
