import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AuthenticatedLayout from '../components/layout/AuthenticatedLayout';

// Mock useNavigate and useLocation from react-router-dom
const mockedNavigate = jest.fn();
let mockPathname = '/dashboard';

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockedNavigate,
  useLocation: () => ({ pathname: mockPathname }),
  Outlet: () => <div data-testid="outlet-content">Outlet Content</div>,
}));

describe('AuthenticatedLayout Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockPathname = '/dashboard';
  });

  test('renders left-hand navigation menu with Dashboard and Projects links', () => {
    render(
      <BrowserRouter>
        <AuthenticatedLayout />
      </BrowserRouter>
    );

    expect(screen.getByText('App Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Projects')).toBeInTheDocument();
    expect(screen.getByTestId('outlet-content')).toBeInTheDocument();
  });

  test('navigates to projects when Projects link is clicked', () => {
    render(
      <BrowserRouter>
        <AuthenticatedLayout />
      </BrowserRouter>
    );

    const projectsButton = screen.getByText('Projects');
    fireEvent.click(projectsButton);

    expect(mockedNavigate).toHaveBeenCalledWith('/projects');
  });

  test('navigates to dashboard when Dashboard link is clicked', () => {
    mockPathname = '/projects';
    render(
      <BrowserRouter>
        <AuthenticatedLayout />
      </BrowserRouter>
    );

    const dashboardButton = screen.getByText('Dashboard');
    fireEvent.click(dashboardButton);

    expect(mockedNavigate).toHaveBeenCalledWith('/dashboard');
  });

  test('highlights active link correctly based on current route', () => {
    mockPathname = '/projects';
    render(
      <BrowserRouter>
        <AuthenticatedLayout />
      </BrowserRouter>
    );

    const projectsButton = screen.getByText('Projects').closest('div[role="button"]');
    expect(projectsButton).toHaveClass('Mui-selected');
  });
});
