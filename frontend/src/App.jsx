import { BrowserRouter, Route, Routes, useInRouterContext } from 'react-router-dom';

import Layout from './components/Layout';
import About from './pages/About';
import Contact from './pages/Contact';
import Home from './pages/Home';
import NotFound from './pages/NotFound';

/**
 * Public route table.
 * Every page is rendered as a child of the shared Layout route so that the
 * responsive navbar (and footer) stay visible on each page.
 *
 * Authenticated routes (/register, /dashboard) are added in a later phase.
 */
function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

/**
 * App renders the route table. When the application is already mounted inside a
 * router (for example a MemoryRouter in tests, or a BrowserRouter in main.jsx)
 * the existing router context is reused; otherwise a BrowserRouter is created.
 */
export default function App() {
  const insideRouter = useInRouterContext();

  if (insideRouter) {
    return <AppRoutes />;
  }

  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export { AppRoutes };
