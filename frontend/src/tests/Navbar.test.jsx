import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Layout from '../components/Layout';

const mockLogout = vi.fn();
const mockAuth = { user: null, logout: mockLogout };

vi.mock('../context/AuthContext', () => ({
  useAuth: () => mockAuth,
}));

function renderNavbar(initialEntries = ['/']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Navbar />
    </MemoryRouter>,
  );
}

function renderLayoutWithRoutes(initialEntries = ['/']) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<div>Home page content</div>} />
          <Route path="/about" element={<div>About page content</div>} />
          <Route path="/contact" element={<div>Contact page content</div>} />
          <Route path="/register" element={<div>Register page content</div>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe('Navbar', () => {
  beforeEach(() => {
    mockAuth.user = null;
    mockLogout.mockReset();
  });

  it('renders the brand and the public navigation links with correct targets', () => {
    renderNavbar();

    const mainNav = screen.getByRole('navigation', { name: /main navigation/i });

    expect(within(mainNav).getByRole('link', { name: 'Home' })).toHaveAttribute('href', '/');
    expect(within(mainNav).getByRole('link', { name: 'About Us' })).toHaveAttribute(
      'href',
      '/about',
    );
    expect(within(mainNav).getByRole('link', { name: 'Contact Us' })).toHaveAttribute(
      'href',
      '/contact',
    );
    expect(screen.getByRole('link', { name: 'MyApp' })).toHaveAttribute('href', '/');
  });

  it('marks the active route with aria-current', () => {
    renderNavbar(['/about']);

    const mainNav = screen.getByRole('navigation', { name: /main navigation/i });
    expect(within(mainNav).getByRole('link', { name: 'About Us' })).toHaveAttribute(
      'aria-current',
      'page',
    );
    expect(within(mainNav).getByRole('link', { name: 'Home' })).not.toHaveAttribute('aria-current');
  });

  it('shows Login and Register when no user is authenticated', () => {
    renderNavbar();

    expect(screen.getByRole('link', { name: 'Login' })).toHaveAttribute('href', '/');
    expect(screen.getByRole('link', { name: 'Register' })).toHaveAttribute('href', '/register');
    expect(screen.queryByRole('button', { name: 'Logout' })).not.toBeInTheDocument();
  });

  it('shows Logout when a user is authenticated and calls the placeholder logout', async () => {
    const user = userEvent.setup();
    mockAuth.user = { id: 1, username: 'tester' };

    renderNavbar();

    expect(screen.queryByRole('link', { name: 'Login' })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Register' })).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Logout' }));
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('opens the drawer from the menu button and exposes the same navigation links', async () => {
    const user = userEvent.setup();
    renderNavbar();

    expect(screen.queryByTestId('mobile-drawer')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /open navigation menu/i }));

    const drawer = await screen.findByTestId('mobile-drawer');
    expect(within(drawer).getByRole('link', { name: 'Home' })).toHaveAttribute('href', '/');
    expect(within(drawer).getByRole('link', { name: 'About Us' })).toHaveAttribute(
      'href',
      '/about',
    );
    expect(within(drawer).getByRole('link', { name: 'Contact Us' })).toHaveAttribute(
      'href',
      '/contact',
    );
    expect(within(drawer).getByRole('link', { name: 'Login' })).toHaveAttribute('href', '/');
    expect(within(drawer).getByRole('link', { name: 'Register' })).toHaveAttribute(
      'href',
      '/register',
    );
  });

  it('navigates and closes the drawer when a drawer link is clicked', async () => {
    const user = userEvent.setup();
    renderLayoutWithRoutes();

    expect(screen.getByText('Home page content')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /open navigation menu/i }));
    const drawer = await screen.findByTestId('mobile-drawer');

    await user.click(within(drawer).getByRole('link', { name: 'Contact Us' }));

    expect(screen.getByText('Contact page content')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.queryByTestId('mobile-drawer')).not.toBeInTheDocument();
    });
  });

  it('navigates between routes using the inline desktop links', async () => {
    const user = userEvent.setup();
    renderLayoutWithRoutes();

    const mainNav = screen.getByRole('navigation', { name: /main navigation/i });
    await user.click(within(mainNav).getByRole('link', { name: 'About Us' }));

    expect(screen.getByText('About page content')).toBeInTheDocument();
    expect(screen.queryByText('Home page content')).not.toBeInTheDocument();
  });
});
