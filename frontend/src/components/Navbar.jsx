import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import MenuIcon from '@mui/icons-material/Menu';
import { useAuth } from '../context/AuthContext';

/**
 * Single source of truth for the public navigation entries.
 * Rendered both in the desktop toolbar and in the mobile drawer.
 */
const navLinks = [
  { label: 'Home', path: '/' },
  { label: 'About Us', path: '/about' },
  { label: 'Contact Us', path: '/contact' },
];

const DRAWER_WIDTH = 260;

// Subtle active-route styling. React Router's NavLink adds the `active`
// class (and aria-current="page") to the rendered element.
const activeLinkSx = {
  '&.active': {
    textDecoration: 'underline',
    textUnderlineOffset: '6px',
    fontWeight: 600,
  },
};

const activeListItemSx = {
  '&.active': {
    fontWeight: 600,
    backgroundColor: 'rgba(25, 118, 210, 0.08)',
  },
};

function Navbar() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const { user, logout } = useAuth();

  const openDrawer = () => setIsDrawerOpen(true);
  const closeDrawer = () => setIsDrawerOpen(false);

  const handleLogout = () => {
    closeDrawer();
    logout();
  };

  const renderDesktopAuthActions = () => {
    if (user) {
      return (
        <Button color="inherit" onClick={handleLogout}>
          Logout
        </Button>
      );
    }

    return (
      <>
        {/* Login lives on the home page per the architecture route table. */}
        <Button color="inherit" component={Link} to="/">
          Login
        </Button>
        <Button color="inherit" variant="outlined" component={Link} to="/register">
          Register
        </Button>
      </>
    );
  };

  const renderDrawerAuthActions = () => {
    if (user) {
      return (
        <ListItem disablePadding>
          <ListItemButton onClick={handleLogout}>
            <ListItemText primary="Logout" />
          </ListItemButton>
        </ListItem>
      );
    }

    return (
      <>
        <ListItem disablePadding>
          <ListItemButton component={Link} to="/" onClick={closeDrawer}>
            <ListItemText primary="Login" />
          </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
          <ListItemButton component={Link} to="/register" onClick={closeDrawer}>
            <ListItemText primary="Register" />
          </ListItemButton>
        </ListItem>
      </>
    );
  };

  return (
    <>
      <AppBar position="static" color="primary" elevation={1}>
        <Toolbar className="flex w-full items-center gap-2 px-2 sm:px-4">
          {/* Mobile: hamburger button (hidden from md upwards) */}
          <IconButton
            edge="start"
            color="inherit"
            aria-label="open navigation menu"
            onClick={openDrawer}
            className="md:hidden"
          >
            <MenuIcon />
          </IconButton>

          <Typography
            variant="h6"
            component={Link}
            to="/"
            className="flex-1 truncate font-semibold no-underline"
            sx={{ color: 'inherit', textDecoration: 'none' }}
          >
            MyApp
          </Typography>

          {/* Desktop: inline navigation links */}
          <nav
            role="navigation"
            aria-label="Main navigation"
            className="hidden items-center gap-1 md:flex"
          >
            {navLinks.map((link) => (
              <Button
                key={link.path}
                color="inherit"
                component={NavLink}
                to={link.path}
                end={link.path === '/'}
                sx={activeLinkSx}
              >
                {link.label}
              </Button>
            ))}
          </nav>

          {/* Desktop: auth actions */}
          <div className="hidden items-center gap-2 md:flex md:pl-4">
            {renderDesktopAuthActions()}
          </div>
        </Toolbar>
      </AppBar>

      {/* Mobile: temporary drawer with the same links + auth actions */}
      <Drawer
        anchor="left"
        open={isDrawerOpen}
        onClose={closeDrawer}
        ModalProps={{ keepMounted: false }}
      >
        <Box
          sx={{ width: DRAWER_WIDTH }}
          role="presentation"
          data-testid="mobile-drawer"
          className="py-2"
        >
          <Typography variant="subtitle1" className="px-4 py-2 font-semibold">
            Menu
          </Typography>
          <Divider />
          <nav role="navigation" aria-label="Mobile navigation">
            <List>
              {navLinks.map((link) => (
                <ListItem key={link.path} disablePadding>
                  <ListItemButton
                    component={NavLink}
                    to={link.path}
                    end={link.path === '/'}
                    onClick={closeDrawer}
                    sx={activeListItemSx}
                  >
                    <ListItemText primary={link.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
            <Divider />
            <List>{renderDrawerAuthActions()}</List>
          </nav>
        </Box>
      </Drawer>
    </>
  );
}

export default Navbar;
