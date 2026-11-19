import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

/**
 * Application shell: renders the Navbar once and the active route inside a
 * responsive, horizontally centred container shared by every routed page.
 * ThemeProvider / CssBaseline / BrowserRouter live in main.jsx and App.jsx.
 */
function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <main className="flex-1 w-full">
        <div className="container mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8 lg:py-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

export default Layout;
