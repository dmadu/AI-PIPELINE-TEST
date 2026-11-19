import { createContext, useContext } from 'react';

/**
 * TEMPORARY PLACEHOLDER.
 *
 * TODO: Replace this module with the real AuthProvider / useAuth implementation
 * in the AuthContext task (user + token state, login/register/logout, token
 * persisted in localStorage under 'auth_token').
 *
 * The exported API ({ user, logout }) intentionally matches the planned
 * useAuth contract so consumers such as Navbar.jsx do not need to change.
 */
const defaultAuthValue = {
  user: null,
  logout: () => {},
};

const AuthContext = createContext(defaultAuthValue);

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthContext;
