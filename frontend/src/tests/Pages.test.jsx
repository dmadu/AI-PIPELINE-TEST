import { fireEvent, render, screen, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import App from '../App';

// The public pages do not consume auth state, but the shared Navbar may.
// Stub useAuth so the page tests stay isolated from the auth provider/API.
vi.mock('../context/AuthContext', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: () => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    }),
  };
});

function renderApp(route = '/') {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <App />
    </MemoryRouter>
  );
}

function clickNavLink(name) {
  const links = screen.getAllByRole('link', { name, hidden: true });
  fireEvent.click(links[0]);
}

describe('public pages routing', () => {
  it('renders the Home page at /', () => {
    renderApp('/');

    expect(screen.getByRole('heading', { name: /welcome to secureauth/i })).toBeInTheDocument();
    expect(screen.getByTestId('home-page')).toBeInTheDocument();
  });

  it('renders the About page at /about', () => {
    renderApp('/about');

    expect(screen.getByRole('heading', { name: /about us/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByTestId('about-page')).toBeInTheDocument();
  });

  it('renders the Contact page with static details at /contact', () => {
    renderApp('/contact');

    expect(screen.getByRole('heading', { name: /contact us/i, level: 1 })).toBeInTheDocument();
    expect(screen.getByText(/support@secureauth\.example/i)).toBeInTheDocument();
    expect(screen.getByText(/\+1 \(555\) 014-7788/)).toBeInTheDocument();
  });

  it('renders the NotFound page for an unknown path and links back to Home', () => {
    renderApp('/does-not-exist');

    expect(screen.getByRole('heading', { name: /404/i })).toBeInTheDocument();
    expect(screen.getByText(/page not found/i)).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('notfound-home-link'));

    expect(screen.getByRole('heading', { name: /welcome to secureauth/i })).toBeInTheDocument();
  });
});

describe('navbar navigation', () => {
  it('navigates from Home to About Us and Contact Us without losing the navbar', () => {
    renderApp('/');

    clickNavLink(/about us/i);
    expect(screen.getByRole('heading', { name: /about us/i, level: 1 })).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /home/i, hidden: true }).length).toBeGreaterThan(0);

    clickNavLink(/contact us/i);
    expect(screen.getByRole('heading', { name: /contact us/i, level: 1 })).toBeInTheDocument();
    expect(screen.getAllByRole('link', { name: /home/i, hidden: true }).length).toBeGreaterThan(0);
  });
});

describe('home auth placeholder slot', () => {
  it('renders the placeholder slot without any form controls', () => {
    renderApp('/');

    const slot = screen.getByTestId('home-auth-slot');
    expect(slot).toBeInTheDocument();
    expect(slot.querySelectorAll('form, input, textarea, select')).toHaveLength(0);

    const page = within(screen.getByTestId('home-page'));
    expect(page.queryAllByRole('textbox')).toHaveLength(0);
  });
});
