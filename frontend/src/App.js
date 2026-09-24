import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import './App.css';

function HomePage() {
  const navigate = useNavigate();

  const handleLogin = () => {
    // Trigger AAF OpenID Connect login endpoint or auth route
    window.location.href = '/api/auth/login';
  };

  return (
    <div className="home-container">
      <header className="app-header">
        <nav className="navbar">
          <div className="nav-brand">
            <Link to="/">Application</Link>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/help">Help</Link>
            </li>
            <li>
              <Link to="/contact">Contact</Link>
            </li>
          </ul>
          <div className="nav-auth">
            <button onClick={handleLogin} className="login-btn">
              Login
            </button>
          </div>
        </nav>
      </header>
      <main className="main-content">
        <div className="hero-section">
          <h1>Welcome to Our Platform</h1>
          <p>Please log in using your institutional credentials to access full features.</p>
          <button onClick={handleLogin} className="hero-login-btn">
            Login with AAF
          </button>
        </div>
      </main>
    </div>
  );
}

function HelpPage() {
  return (
    <div className="page-container">
      <nav className="sub-nav">
        <Link to="/">&larr; Back to Home</Link>
      </nav>
      <h1>Help & Support</h1>
      <p>Find answers to frequently asked questions and guides on how to use the application.</p>
    </div>
  );
}

function ContactPage() {
  return (
    <div className="page-container">
      <nav className="sub-nav">
        <Link to="/">&larr; Back to Home</Link>
      </nav>
      <h1>Contact Us</h1>
      <p>Get in touch with our support team for assistance.</p>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/help" element={<HelpPage />} />
        <Route path="/contact" element={<ContactPage />} />
      </Routes>
    </Router>
  );
}

export default App;
