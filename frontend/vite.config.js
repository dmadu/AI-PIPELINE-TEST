import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

/**
 * Vite configuration for the React 19 SPA.
 *
 * - Dev server binds to 0.0.0.0 so it is reachable from outside a container.
 * - Port 3000 matches the frontend port mapping used by docker-compose.yml.
 * - /api is proxied to the Flask backend so the SPA can call /api/v1 in
 *   development without CORS surprises. The target defaults to the local
 *   backend and can be overridden with VITE_PROXY_TARGET (for example
 *   http://backend:5000 when running inside Docker Compose).
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const proxyTarget = env.VITE_PROXY_TARGET || 'http://localhost:5000';
  const devPort = Number(env.VITE_DEV_PORT || 3000);

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: devPort,
      strictPort: true,
      watch: {
        usePolling: true,
      },
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
        },
      },
    },
    preview: {
      host: '0.0.0.0',
      port: devPort,
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
    },
  };
});
