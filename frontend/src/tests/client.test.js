import { beforeEach, describe, expect, it, vi } from 'vitest';

const { mockInstance, captured } = vi.hoisted(() => {
  const capturedHandlers = { request: [], response: [] };
  const instance = {
    defaults: { headers: {} },
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: {
        use: (onFulfilled, onRejected) => {
          capturedHandlers.request.push({ onFulfilled, onRejected });
        },
      },
      response: {
        use: (onFulfilled, onRejected) => {
          capturedHandlers.response.push({ onFulfilled, onRejected });
        },
      },
    },
  };
  return { mockInstance: instance, captured: capturedHandlers };
});

vi.mock('axios', () => ({
  default: { create: vi.fn(() => mockInstance) },
}));

const axios = (await import('axios')).default;
const clientModule = await import('../api/client.js');

const client = clientModule.default;
const { AUTH_TOKEN_KEY, getToken, setToken, clearToken } = clientModule;

const requestInterceptor = captured.request[0];
const responseInterceptor = captured.response[0];

describe('api/client configuration', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('creates a single axios instance with a baseURL and JSON headers', () => {
    expect(axios.create).toHaveBeenCalledTimes(1);
    const config = axios.create.mock.calls[0][0];
    expect(typeof config.baseURL).toBe('string');
    expect(config.baseURL.length).toBeGreaterThan(0);
    expect(config.baseURL.endsWith('/')).toBe(false);
    expect(config.headers['Content-Type']).toBe('application/json');
    expect(client).toBe(mockInstance);
  });

  it('registers one request and one response interceptor', () => {
    expect(captured.request).toHaveLength(1);
    expect(captured.response).toHaveLength(1);
  });
});

describe('token helpers', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('uses the auth_token localStorage key', () => {
    expect(AUTH_TOKEN_KEY).toBe('auth_token');
  });

  it('stores, reads and clears the token', () => {
    expect(getToken()).toBeNull();
    setToken('jwt-value');
    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBe('jwt-value');
    expect(getToken()).toBe('jwt-value');
    clearToken();
    expect(getToken()).toBeNull();
  });
});

describe('request interceptor', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('attaches a Bearer token when one is stored', () => {
    setToken('abc123');
    const config = requestInterceptor.onFulfilled({ headers: {}, url: '/auth/me' });
    expect(config.headers.Authorization).toBe('Bearer abc123');
  });

  it('omits the Authorization header when no token is stored', () => {
    const config = requestInterceptor.onFulfilled({ headers: {}, url: '/auth/login' });
    expect(config.headers.Authorization).toBeUndefined();
  });
});

describe('response interceptor', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it('passes successful responses through unchanged', () => {
    const response = { status: 200, data: { data: { id: 1 } } };
    expect(responseInterceptor.onFulfilled(response)).toBe(response);
  });

  it('normalises a backend error envelope including fields', async () => {
    const axiosError = {
      response: {
        status: 400,
        data: {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Validation failed',
            fields: { password: 'Password must be at least 8 characters long' },
          },
        },
      },
    };

    await expect(responseInterceptor.onRejected(axiosError)).rejects.toMatchObject({
      code: 'VALIDATION_ERROR',
      message: 'Validation failed',
      fields: { password: 'Password must be at least 8 characters long' },
      status: 400,
      originalError: axiosError,
    });
  });

  it('normalises an envelope without fields to an empty object', async () => {
    const axiosError = {
      response: {
        status: 409,
        data: { error: { code: 'DUPLICATE_EMAIL', message: 'Email already registered' } },
      },
    };

    await expect(responseInterceptor.onRejected(axiosError)).rejects.toMatchObject({
      code: 'DUPLICATE_EMAIL',
      message: 'Email already registered',
      fields: {},
      status: 409,
    });
  });

  it('falls back to INTERNAL_ERROR for unexpected non-envelope bodies', async () => {
    const axiosError = {
      response: { status: 500, data: '<html><body>Server Error</body></html>' },
    };

    const rejected = await responseInterceptor.onRejected(axiosError).catch((err) => err);
    expect(rejected.code).toBe('INTERNAL_ERROR');
    expect(typeof rejected.message).toBe('string');
    expect(rejected.message.length).toBeGreaterThan(0);
    expect(rejected.fields).toEqual({});
    expect(rejected.status).toBe(500);
  });

  it('normalises network failures with no response', async () => {
    const axiosError = { message: 'Network Error', request: {} };

    const rejected = await responseInterceptor.onRejected(axiosError).catch((err) => err);
    expect(rejected.code).toBe('NETWORK_ERROR');
    expect(rejected.status).toBe(0);
    expect(rejected.fields).toEqual({});
    expect(typeof rejected.message).toBe('string');
  });

  it('clears the stored token on 401 and still rejects', async () => {
    setToken('expired-token');
    const axiosError = {
      response: {
        status: 401,
        data: { error: { code: 'TOKEN_INVALID', message: 'Invalid or expired token' } },
      },
    };

    await expect(responseInterceptor.onRejected(axiosError)).rejects.toMatchObject({
      code: 'TOKEN_INVALID',
      status: 401,
    });
    expect(window.localStorage.getItem(AUTH_TOKEN_KEY)).toBeNull();
  });
});
