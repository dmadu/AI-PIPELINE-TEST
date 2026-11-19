import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  AppBar,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Toolbar,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '../context/AuthContext';

const NAV_LINKS = [
  { label: 'Home', to: '/' },
  { label: 'About Us', to: '/about' },
  { label: 'Contact Us', to: '/contact' },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen((prevState) => !prevState);
  };

  const handleLogout = () => {
    logout();
    setMobileOpen(false);
  };

  const navItems = (
    <Box onClick={handleDrawerToggle} sx={{ textAlign: 'center' }}>
      <Typography variant="h6" sx={{ my: 2 }}>
        MyApp
      </Typography>
      <Divider />
      <List>
        {NAV_LINKS.map((item) => (
          <ListItem key={item.label} disablePadding>
            <ListItemButton component={RouterLink} to={item.to} sx={{ textAlign: 'center' }}>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
        {!user ? (
          <>
            <ListItem disablePadding>
              <ListItemButton component={RouterLink} to="/" sx={{ textAlign: 'center' }}>
                <ListItemText primary="Login" />
              </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
              <ListItemButton component={RouterLink} to="/register" sx={{ textAlign: 'center' }}>
                <ListItemText primary="Register" />
              </ListItemButton>
            </ListItem>
          </>
        ) : (
          <ListItem disablePadding>
            <ListItemButton onClick={handleLogout} sx={{ textAlign: 'center' }}>
              <ListItemText primary="Logout" />
            </ListItemButton>
          </ListItem>
        )}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar component="nav" position="sticky">
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open navigation menu"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              display: { xs: 'none', sm: 'block' },
              textDecoration: 'none',
              color: 'inherit',
            }}
          >
            MyApp
          </Typography>
          <Box sx={{ display: { xs: 'none', md: 'block' } }} role="navigation" aria-label="main navigation">
            {NAV_LINKS.map((item) => (
              <Button key={item.label} component={RouterLink} to={item.to} color="inherit">
                {item.label}
              </Button>
            ))}
            {!user ? (
              <>
                <Button component={RouterLink} to="/" color="inherit">
                  Login
                </Button>
                <Button component={RouterLink} to="/register" color="inherit">
                  Register
                </Button>
              </>
            ) : (
              <Button onClick={handleLogout} color="inherit">
                Logout
              </Button>
            )}
          </Box>
        </Toolbar>
      </AppBar>
      <nav>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 240 },
          }}
          data-testid="mobile-drawer"
        >
          {navItems}
        </Drawer>
      </nav>
    </Box>
  );
}
