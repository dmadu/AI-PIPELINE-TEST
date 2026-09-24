import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import FolderIcon from '@mui/icons-material/Folder';
import LogoutIcon from '@mui/icons-material/Logout';

const drawerWidth = 260;

export const AuthenticatedLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    {
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard',
    },
    {
      text: 'Projects',
      icon: <FolderIcon />,
      path: '/projects',
    },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    if (mobileOpen) {
      setMobileOpen(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    navigate('/login');
  };

  const drawerContent = (
    <div className="flex flex-col h-full bg-slate-900 text-slate-100">
      <div className="flex items-center justify-center h-16 px-6 border-b border-slate-800">
        <Typography variant="h6" noWrap component="div" className="font-bold tracking-wider text-indigo-400">
          App Dashboard
        </Typography>
      </div>
      <Divider className="bg-slate-800" />
      <List className="flex-1 px-3 py-4 space-y-1">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding className="rounded-lg overflow-hidden">
              <ListItemButton
                selected={isActive}
                onClick={() => handleNavigation(item.path)}
                className={`rounded-lg transition-colors ${
                  isActive
                    ? '!bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                    : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                }`}
              >
                <ListItemIcon className={`min-w-[40px] ${isActive ? 'text-white' : 'text-slate-400'}`}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} primaryTypographyProps={{ className: 'font-medium' }} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
      <Divider className="bg-slate-800" />
      <div className="p-3">
        <ListItem disablePadding className="rounded-lg overflow-hidden">
          <ListItemButton
            onClick={handleLogout}
            className="rounded-lg text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition-colors"
          >
            <ListItemIcon className="min-w-[40px] text-rose-400">
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Logout" primaryTypographyProps={{ className: 'font-medium' }} />
          </ListItemButton>
        </ListItem>
      </div>
    </div>
  );

  return (
    <Box className="flex h-screen bg-slate-50">
      {/* Top AppBar for mobile */}
      <AppBar
        position="fixed"
        className="bg-white text-slate-800 shadow-sm border-b border-slate-200 lg:hidden"
        elevation={0}
      >
        <Toolbar className="flex justify-between">
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            className="mr-2 text-slate-600 hover:bg-slate-100"
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" className="font-bold text-slate-800">
            {menuItems.find((item) => item.path === location.pathname)?.text || 'Application'}
          </Typography>
          <div className="w-10" />
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box component="nav" className="lg:flex-shrink-0 lg:w-[260px]" aria-label="mailbox folders">
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', lg: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, border: 'none' },
          }}
        >
          {drawerContent}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', lg: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth, borderRight: '1px solid #e2e8f0' },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      {/* Main Content Outlet */}
      <Box
        component="main"
        className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-slate-50 pt-16 lg:pt-0"
      >
        <div className="flex-1 p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </div>
      </Box>
    </Box>
  );
};

export default AuthenticatedLayout;
