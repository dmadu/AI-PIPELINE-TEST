import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Home from '../pages/Home';

const mockNavigate = vi.fn();
const mockLogin = vi.fn();

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, useNavigate: () => mockNavigate };
});

vi.mock('../context/AuthContext', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useAuth: () => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      login: mockLogin,
      register: vi.fn(),
      logout: vi.fn(),
    }),
  };
});

const renderHome = () =>
  render(
    <MemoryRouter initialEntries={['/']}>
      <Home />
    </MemoryRouter>,
  );

const fillForm = ({ identifier, password }) => {
  fireEvent.change(screen.getByLabelText(/username or email/i), {
    target: { value: identifier },
  });
  fireEvent.change(screen.getByLabelText(/^password$/i), {
    target: { value: password },
  });
};

describe('Home page login form', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
    mockLogin.mockReset();
  });

  it('renders the login form and a link to the registration page', () => {
    renderHome();

    expect(screen.getByLabelText(/username or email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toHaveAttribute('type', 'password');

    const registerLink = screen.getByRole('link', { name: /create an account/i });
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('shows required messages and does not call login when fields are empty', async () => {
    renderHome();

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(await screen.findByText(/username or email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    expect(mockLogin).not.toHaveBeenCalled();
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('calls login once with identifier and password and navigates to the dashboard', async () => {
    mockLogin.mockResolvedValue({
      access_token: 'token',
      user: { id: 1, username: 'alice', email: 'alice@example.com' },
    });

    renderHome();
    fillForm({ identifier: 'alice', password: 'Passw0rd!' });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => expect(mockLogin).toHaveBeenCalledTimes(1));
    expect(mockLogin).toHaveBeenCalledWith({ identifier: 'alice', password: 'Passw0rd!' });
    await waitFor(() =>
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard', { replace: true }),
    );
  });

  it('renders the generic invalid-credentials message and stays on the home page', async () => {
    mockLogin.mockRejectedValue({
      code: 'INVALID_CREDENTIALS',
      message: 'Invalid username/email or password',
    });

    renderHome();
    fillForm({ identifier: 'alice@example.com', password: 'wrong-password' });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    expect(
      await screen.findByText(/invalid username\/email or password/i),
    ).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();
    expect(screen.getByLabelText(/username or email/i)).toHaveValue('alice@example.com');
  });
});
