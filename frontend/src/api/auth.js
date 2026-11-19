import client from './client.js';

/**
 * Unwrap the backend success envelope ({ "data": ... }).
 * @param {{data?: {data?: unknown}}} response Axios response.
 * @returns {unknown} The contents of the envelope's data field, or null.
 */
function unwrap(response) {
  const body = response && response.data;
  if (body && typeof body === 'object' && 'data' in body) {
    return body.data;
  }
  return body ?? null;
}

/**
 * Register a new account.
 * @param {{email: string, username: string, password: string}} payload Registration fields.
 * @returns {Promise<Object>} The created user object.
 * @throws {{code: string, message: string, fields: Object, status: number}} Normalised API error.
 */
export async function registerUser(payload) {
  const response = await client.post('/auth/register', payload);
  return unwrap(response);
}

/**
 * Authenticate with a username/email identifier and password.
 * @param {{identifier: string, password: string}} payload Login credentials.
 * @returns {Promise<{access_token: string, user: Object}>} Token and user payload.
 * @throws {{code: string, message: string, fields: Object, status: number}} Normalised API error.
 */
export async function loginUser(payload) {
  const response = await client.post('/auth/login', payload);
  return unwrap(response);
}

/**
 * Fetch the profile of the currently authenticated user (Bearer token added by the client).
 * @returns {Promise<Object>} The current user object.
 * @throws {{code: string, message: string, fields: Object, status: number}} Normalised API error.
 */
export async function getCurrentUser() {
  const response = await client.get('/auth/me');
  return unwrap(response);
}
