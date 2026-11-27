import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Container, Button, Typography, Box } from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import SpeedIcon from '@mui/icons-material/Speed';
import StorageIcon from '@mui/icons-material/Storage';

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="py-12">
      <Container maxWidth="lg">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto py-12">
          <Typography variant="h2" component="h1" className="font-extrabold text-slate-900 tracking-tight mb-4" sx={{ fontSize: { xs: '2.5rem', md: '3.75rem' } }}>
            Modern Full-Stack <span className="text-indigo-600">Architecture</span>
          </Typography>
          <Typography variant="body1" className="text-lg text-slate-600 mb-8">
            Production-ready application powered by React 19, Material UI, Tailwind CSS, Flask 3.11, PostgreSQL, and JWT Authentication.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            {user ? (
              <Button variant="contained" size="large" component={Link} to="/dashboard" sx={{ bgcolor: '#4f46e5', '&:hover': { bgcolor: '#4338ca' }, px: 4, py: 1.5, fontSize: '1rem' }}>
                Go to Dashboard
              </Button>
            ) : (
              <>
                <Button variant="contained" size="large" component={Link} to="/register" sx={{ bgcolor: '#4f46e5', '&:hover': { bgcolor: '#4338ca' }, px: 4, py: 1.5, fontSize: '1rem' }}>
                  Get Started
                </Button>
                <Button variant="outlined" size="large" component={Link} to="/login" sx={{ borderColor: '#4f46e5', color: '#4f46e5', px: 4, py: 1.5, fontSize: '1rem' }}>
                  Sign In
                </Button>
              </>
            )}
          </Box>
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mt-16">
          <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center mx-auto mb-4">
              <SecurityIcon />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">Secure Auth</h3>
            <p className="text-slate-600">
              Protected routes, Flask-Bcrypt password hashing, and robust JWT token-based session management.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center mx-auto mb-4">
              <SpeedIcon />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">High Performance</h3>
            <p className="text-slate-600">
              React 19 single-page application styled seamlessly with Tailwind utilities and Material UI components.
            </p>
          </div>

          <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center mx-auto mb-4">
              <StorageIcon />
            </div>
            <h3 className="text-xl font-bold text-slate-900 mb-2">PostgreSQL Ready</h3>
            <p className="text-slate-600">
              Reliable database persistence handled via SQLAlchemy ORM and structured Alembic migrations.
            </p>
          </div>
        </div>
      </Container>
    </div>
  );
}
