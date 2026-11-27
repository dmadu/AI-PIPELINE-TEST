import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Container, Typography, Button, Box } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import EmailIcon from '@mui/icons-material/Email';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="py-12">
      <Container maxWidth="lg">
        <div className="mb-8">
          <Typography variant="h4" component="h1" className="font-bold text-slate-900">
            Welcome back, <span className="text-indigo-600">{user?.username}</span>!
          </Typography>
          <p className="text-slate-600 mt-1">
            Here is your secure dashboard overview.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center">
              <AccountCircleIcon />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium">Username</p>
              <p className="text-lg font-bold text-slate-900">{user?.username}</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center">
              <EmailIcon />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium">Email Address</p>
              <p className="text-lg font-bold text-slate-900 truncate max-w-[200px]">{user?.email}</p>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex items-center gap-4">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-lg flex items-center justify-center">
              <CalendarTodayIcon />
            </div>
            <div>
              <p className="text-sm text-slate-500 font-medium">Member Since</p>
              <p className="text-base font-bold text-slate-900">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          <Typography variant="h6" className="font-bold text-slate-900 mb-2">
            Account Actions
          </Typography>
          <p className="text-slate-600 mb-4">
            You are currently logged in with a valid JWT session token.
          </p>
          <Button
            variant="outlined"
            color="error"
            onClick={logout}
          >
            Sign Out of Session
          </Button>
        </div>
      </Container>
    </div>
  );
}
