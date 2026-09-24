import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('renders public home page with navigation and login button', () => {
  render(<App />);
  
  // Check branding / welcome
  expect(screen.getByText(/Welcome to Our Platform/i)).toBeInTheDocument();
  
  // Check Help and Contact links
  expect(screen.getByText('Help')).toBeInTheDocument();
  expect(screen.getByText('Contact')).toBeInTheDocument();
  
  // Check Login buttons
  const loginButtons = screen.getAllByRole('button', { name: /login/i });
  expect(loginButtons.length).toBeGreaterThan(0);
});

test('navigates to help page when Help is clicked', () => {
  render(<App />);
  
  fireEvent.click(screen.getByText('Help'));
  
  expect(screen.getByText(/Help & Support/i)).toBeInTheDocument();
});

test('navigates to contact page when Contact is clicked', () => {
  render(<App />);
  
  fireEvent.click(screen.getByText('Contact'));
  
  expect(screen.getByText(/Contact Us/i)).toBeInTheDocument();
});
