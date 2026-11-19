import axios from 'axios';

/**
 * localStorage key where the JWT access token is persisted.
 * AuthContext and the interceptors below must share this single definition.
 * @type {string}
 */
export const AUTH_TOKEN_KEY = 'auth_token';

/** Error code used when the request never reached the API. */
export const NETWORK_ERROR_CODE = 'NETWORK_ERROR';

/** Error code used when the API answered with an unexpected body. */
export const INTERNAL_ERROR_CODE = 'INTERNAL_ERROR';

const DEFAULT_BASE_URL = 'http://localhost:5000/api/v1';
const REQUEST_TIMEOUT_MS = 15000;

const NETWORK_ERROR_MESSAGE =
  'Unable to reach the server. Please check your connection and try again.';
const TIMEOUT_ERROR_MESSAGE = 'The server took too long to respond. Please try again.';
const GENERIC_ERROR_MESSAGE = 'Something went wrong. Please try again.';

const STATUS_MESSAGES = {
  400: 'The submitted data is invalid.',
  401: 'Your session is no longer valid. Please sign in again.',
  403: 'You are not allowed to perform this action.',
  404: 'The requested resource was not found.',
  409: 'That record already exists.',
  422: 'The submitted data is invalid.',
  500: 'Something went wrong on the server. Please try again.',
};

/**
 * Safely resolve the browser localStorage, returning null when unavailable
 * (SSR, hardened privacy settings, non-browser test environments).
 * @returns {Storage|null}
 */
function getStorage() {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return null;
    }
    return window.localStorage;
  } catch (err) {
    return null;
  }
}

/**
 * Read the persisted JWT access token.
 * @returns {string|null} The stored token, or null when none is available.
 */
export function getToken() {
  const storage = getStorage();
  if (!storage) {
    return null;
  }
  try {
    const token = storage.getItem(AUTH_TOKEN_KEY);
    return token && token.length > 0 ? token : null;
  } catch (err) {
    return null;
  }
}

/**
 * Persist the JWT access token. Passing an empty value clears it instead.
 * @param {string|null|undefined} token Raw JWT access token.
 * @returns {void}
 */
export function setToken(token) {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  try {
    if (typeof token === 'string' && token.length > 0) {
      storage.setItem(AUTH_TOKEN_KEY, token);
    } else {
      storage.removeItem(AUTH_TOKEN_KEY);
    }
  } catch (err) {
    /* storage unavailable - nothing to persist */
  }
}

/**
 * Remove the persisted JWT access token.
 * @returns {void}
 */
export function clearToken() {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  try {
    storage.removeItem(AUTH_TOKEN_KEY);
  } catch (err) {
    /* storage unavailable - nothing to clear */
  }
}

/**
 * Resolve the API base URL from the Vite environment with a local fallback.
 * @returns {string} Base URL without a trailing slash.
 */
function resolveBaseUrl() {
  let configured;
  try {
    configured = import.meta.env ? import.meta.env.VITE_API_BASE_URL : undefined;
  } catch (err) {
    configured = undefined;
  }
  if (typeof configured === 'string' && configured.trim().length > 0) {
    return configured.trim().replace(/\/+$/, '');
  }
  return DEFAULT_BASE_URL;
}

/**
 * Pick a readable message for a status code when the API gave us none.
 * @param {number} status HTTP status code.
 * @returns {string} Human readable fallback message.
 */
function messageForStatus(status) {
  return STATUS_MESSAGES[status] || GENERIC_ERROR_MESSAGE;
}

/**
 * Convert any axios failure into the single normalised error shape used by the UI.
 * Shape: { code, message, fields, status, originalError }.
 * @param {unknown} error Raw axios error (or anything thrown by an interceptor).
 * @returns {{code: string, message: string, fields: Object, status: number, originalError: unknown}}
 */
export function normaliseError(error) {
  const response = error && typeof error === 'object' ? error.response : undefined;

  if (!response) {
    const isTimeout =
      (error && error.code === 'ECONNABORTED') ||
      (error && typeof error.message === 'string' && error.message.toLowerCase().includes('timeout'));
    return {
      code: NETWORK_ERROR_CODE,
      message: isTimeout ? TIMEOUT_ERROR_MESSAGE : NETWORK_ERROR_MESSAGE,
      fields: {},
      status: 0,
      originalError: error ?? null,
    };
  }

  const status = typeof response.status === 'number' ? response.status : 0;
  const body = response.data;
  const envelope = body && typeof body === 'object' && !Array.isArray(body) ? body.error : null;

  if (envelope && typeof envelope === 'object' && !Array.isArray(envelope)) {
    const fields =
      envelope.fields && typeof envelope.fields === 'object' && !Array.isArray(envelope.fields)
        ? envelope.fields
        : {};
    return {
      code: typeof envelope.code === 'string' && envelope.code ? envelope.code : INTERNAL_ERROR_CODE,
      message:
        typeof envelope.message === 'string' && envelope.message
          ? envelope.message
          : messageForStatus(status),
      fields,
      status,
      originalError: error,
    };
  }

  return {
    code: INTERNAL_ERROR_CODE,
    message: messageForStatus(status),
    fields: {},
    status,
    originalError: error,
  };
}

const client = axios.create({
  baseURL: resolveBaseUrl(),
  timeout: REQUEST_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

client.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      if (config.headers && typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        config.headers = { ...(config.headers || {}), Authorization: `Bearer ${token}` };
      }
    }
    return config;
  },
  (error) => Promise.reject(normaliseError(error)),
);

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const normalised = normaliseError(error);
    if (normalised.status === 401) {
      // Drop the stale/invalid token; redirecting is ProtectedRoute/AuthContext's job.
      clearToken();
    }
    return Promise.reject(normalised);
  },
);

export default client;
