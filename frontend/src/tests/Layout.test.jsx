import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Layout from '../components/Layout';

vi.mock('../context/AuthContext', () => ({
  useAuth: () => ({ user: null, logout: () => {} }),
}));

describe('Layout', () => {
  it('renders the navbar once and the routed outlet content', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<div>Outlet content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getAllByRole('navigation', { name: /main navigation/i })).toHaveLength(1);
    expect(screen.getByText('Outlet content')).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
