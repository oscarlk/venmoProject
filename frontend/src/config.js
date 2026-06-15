// Base URL for the Flask backend. Set VITE_API_URL in production (Vercel env);
// falls back to the local dev server.
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
