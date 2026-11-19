/**
 * Authentication state layer for the SPA.
 *
 * Holds the current `user`, the JWT `token` and an `loading` flag while the
 * session is rehydrated from localStorage on a cold start. All HTTP work is
 * delegated to the wrappers in `src/api/auth.js`; the axios client
 * (`src/api/client.js`) stays the single place that reads the stored token for
 * outgoing requests and clears it on a 401 response.
 */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  loginUser as loginRequest,
  getCurrentUser as fetchCurrentUser,
  registerUser as registerRequest,
} from '../api/auth';

/** localStorage key used to persist the access token (see docs/ARCHITECTURE.md). */
export const AUTH_TOKEN_KEY = 'auth_token';

/** @returns {string|null} the persisted access token, if any. */
const readStoredToken = () => {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY) || null;
  } catch (error) {
    return null;
  }
};

/** Persists the access token. */
const writeStoredToken = (token) => {
  try {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  } catch (error) {
    /* storage unavailable - keep the in-memory token only */
  }
};

/** Removes the persisted access token. */
const removeStoredToken = () => {
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  } catch (error) {
    /* storage unavailable - nothing to clean up */
  }
};

/**
 * The API wrappers may return either the user object itself or an envelope
 * containing it ({ user: {...} }). Normalise both shapes.
 */
const extractUser = (payload) => {
  if (!payload) return null;
  if (typeof payload === 'object' && payload.user) return payload.user;
  return payload;
};

const AuthContext = createContext(null);

/**
 * Provides authentication state and actions to the component tree.
 *
 * @param {{ children: React.ReactNode }} props
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => readStoredToken());
  const [loading, setLoading] = useState(true);

  /** Clears every trace of the session (state + localStorage). */
  const clearSession = useCallback(() => {
    setUser(null);
    setToken(null);
    removeStoredToken();
  }, []);

  // Rehydrate the session on mount when a token is already persisted.
  useEffect(() => {
    let cancelled = false;
    const storedToken = readStoredToken();

    if (!storedToken) {
      setLoading(false);
      return undefined;
    }

    setToken(storedToken);

    (async () => {
      try {
        const currentUser = extractUser(await fetchCurrentUser());
        if (!cancelled) {
          setUser(currentUser);
        }
      } catch (error) {
        // Expired / invalid token - drop it silently.
        if (!cancelled) {
          clearSession();
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [clearSession]);

  /**
   * Authenticates the user and persists the issued access token.
   *
   * @param {string} identifier username or email
   * @param {string} password raw password
   * @returns {Promise<object>} the authenticated user
   */
  const login = useCallback(async (identifier, password) => {
    const result = await loginRequest({ identifier, password });
    const accessToken = (result && (result.access_token || result.token)) || null;
    const nextUser = extractUser(result && result.user ? result.user : null);

    if (accessToken) {
      writeStoredToken(accessToken);
    }
    setToken(accessToken);
    setUser(nextUser);

    return nextUser;
  }, []);

  /**
   * Creates a new account. Registration does not issue a token, so the session
   * state is left untouched; the caller decides whether to redirect or log in.
   *
   * @param {{ email: string, username: string, password: string }} payload
   * @returns {Promise<object>} the created user
   */
  const register = useCallback(async (payload) => {
    const { email, username, password } = payload || {};
    const created = await registerRequest({ email, username, password });
    return extractUser(created);
  }, []);

  /** Ends the session. Safe to call when already logged out. */
  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const value = useMemo(
    () => ({
      user,
      token,
      loading,
      initialising: loading,
      isAuthenticated: Boolean(token && user),
      login,
      register,
      logout,
    }),
    [user, token, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Accessor for the authentication context.
 *
 * @throws {Error} when used outside of <AuthProvider>.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthContext;
