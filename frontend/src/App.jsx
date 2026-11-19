import { Link, Route, Routes } from 'react-router-dom';

/**
 * Temporary placeholder used by every route until the real page components
 * (src/pages/*) arrive in later Phase 3 tasks. Each <Route element> below is
 * trivially replaceable by its page component.
 */
function Placeholder({ title }) {
  return (
    <section className="mx-auto max-w-3xl p-8">
      <h1 className="text-3xl font-semibold text-slate-800">{title}</h1>
      <p className="mt-2 text-slate-600">
        This placeholder will be replaced by the real page component.
      </p>
      <nav className="mt-6 flex flex-wrap gap-4 text-sm text-blue-700">
        <Link to="/">Home</Link>
        <Link to="/about">About Us</Link>
        <Link to="/contact">Contact Us</Link>
        <Link to="/register">Register</Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>
    </section>
  );
}

/**
 * Route table only - providers (theme, router, auth) live in main.jsx.
 */
function App() {
  return (
    <Routes>
      <Route path="/" element={<Placeholder title="Home" />} />
      <Route path="/about" element={<Placeholder title="About Us" />} />
      <Route path="/contact" element={<Placeholder title="Contact Us" />} />
      <Route path="/register" element={<Placeholder title="Register" />} />
      <Route path="/dashboard" element={<Placeholder title="Dashboard" />} />
      <Route path="*" element={<Placeholder title="404 - Page Not Found" />} />
    </Routes>
  );
}

export default App;
