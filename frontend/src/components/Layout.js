import React, { useState } from 'react';
import { Outlet, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Container
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [mobileAnchorEl, setMobileAnchorEl] = useState(null);

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleMobileMenu = (event) => {
    setMobileAnchorEl(event.currentTarget);
  };

  const handleMobileClose = () => {
    setMobileAnchorEl(null);
  };

  const handleLogout = () => {
    handleClose();
    handleMobileClose();
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <AppBar position="static" elevation={1} sx={{ backgroundColor: '#ffffff', color: '#0f172a' }}>
        <Container maxWidth="lg">
          <Toolbar disableGutters className="flex justify-between">
            <Typography
              variant="h6"
              component={Link}
              to="/"
              sx={{
                fontWeight: 700,
                color: 'inherit',
                textDecoration: 'none',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <span className="text-indigo-600">FullStack</span>App
            </Typography>

            {/* Desktop Navigation Links */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 2 }}>
              <Button color="inherit" component={Link} to="/">Home</Button>
              <Button color="inherit" component={Link} to="/about">About</Button>
              <Button color="inherit" component={Link} to="/contact">Contact</Button>
              {user && (
                <Button color="inherit" component={Link} to="/dashboard" sx={{ fontWeight: 600, color: '#4f46e5' }}>
                  Dashboard
                </Button>
              )}
            </Box>

            {/* Desktop Auth Section */}
            <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 1.5 }}>
              {user ? (
                <div>
                  <IconButton
                    size="large"
                    aria-label="account of current user"
                    aria-controls="menu-appbar"
                    aria-haspopup="true"
                    onClick={handleMenu}
                    color="inherit"
                  >
                    <Avatar sx={{ width: 36, height: 36, bgcolor: '#4f46e5', fontSize: '1rem' }}>
                      {user.username?.charAt(0).toUpperCase()}
                    </Avatar>
                  </IconButton>
                  <Menu
                    id="menu-appbar"
                    anchorEl={anchorEl}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    keepMounted
                    transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                    open={Boolean(anchorEl)}
                    onClose={handleClose}
                  >
                    <MenuItem onClick={() => { handleClose(); navigate('/dashboard'); }}>Dashboard</MenuItem>
                    <MenuItem onClick={handleLogout}>Logout</MenuItem>
                  </Menu>
                </div>
              ) : (
                <>
                  <Button variant="outlined" component={Link} to="/login" sx={{ borderColor: '#4f46e5', color: '#4f46e5' }}>
                    Login
                  </Button>
                  <Button variant="contained" component={Link} to="/register" sx={{ bgcolor: '#4f46e5', '&:hover': { bgcolor: '#4338ca' } }}>
                    Register
                  </Button>
                </>
              )}
            </Box>

            {/* Mobile Menu Icon */}
            <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
              <IconButton
                size="large"
                aria-label="menu"
                aria-controls="menu-mobile"
                aria-haspopup="true"
                onClick={handleMobileMenu}
                color="inherit"
              >
                <MenuIcon />
              </IconButton>
              <Menu
                id="menu-mobile"
                anchorEl={mobileAnchorEl}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                keepMounted
                transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                open={Boolean(mobileAnchorEl)}
                onClose={handleMobileClose}
              >
                <MenuItem onClick={() => { handleMobileClose(); navigate('/'); }}>Home</MenuItem>
                <MenuItem onClick={() => { handleMobileClose(); navigate('/about'); }}>About</MenuItem>
                <MenuItem onClick={() => { handleMobileClose(); navigate('/contact'); }}>Contact</MenuItem>
                {user ? (
                  <>
                    <MenuItem onClick={() => { handleMobileClose(); navigate('/dashboard'); }}>Dashboard</MenuItem>
                    <MenuItem onClick={handleLogout}>Logout</MenuItem>
                  </>
                ) : (
                  <>
                    <MenuItem onClick={() => { handleMobileClose(); navigate('/login'); }}>Login</MenuItem>
                    <MenuItem onClick={() => { handleMobileClose(); navigate('/register'); }}>Register</MenuItem>
                  </>
                )}
              </Menu>
            </Box>
          </Toolbar>
        </Container>
      </AppBar>

      {/* Main Content */}
      <main className="flex-grow">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-sm text-slate-500">
        <Container maxWidth="lg">
          <p>© {new Date().getFullYear()} FullStack Application. All rights reserved.</p>
        </Container>
      </footer>
    </div>
  );
}
