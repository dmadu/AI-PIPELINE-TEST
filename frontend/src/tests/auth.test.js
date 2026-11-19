import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../api/client.js', () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

const client = (await import('../api/client.js')).default;
const { registerUser, loginUser, getCurrentUser } = await import('../api/auth.js');

describe('api/auth', () => {
  beforeEach(() => {
    client.get.mockReset();
    client.post.mockReset();
  });

  it('registerUser posts to /auth/register and returns the unwrapped user', async () => {
    const user = { id: 1, username: 'alice', email: 'alice@example.com' };
    client.post.mockResolvedValue({ status: 201, data: { data: user } });

    const payload = { email: 'alice@example.com', username: 'alice', password: 'Passw0rd!' };
    const result = await registerUser(payload);

    expect(client.post).toHaveBeenCalledWith('/auth/register', payload);
    expect(result).toEqual(user);
  });

  it('loginUser posts to /auth/login and returns the token and user', async () => {
    const data = { access_token: 'jwt-token', user: { id: 1, username: 'alice' } };
    client.post.mockResolvedValue({ status: 200, data: { data } });

    const payload = { identifier: 'alice', password: 'Passw0rd!' };
    const result = await loginUser(payload);

    expect(client.post).toHaveBeenCalledWith('/auth/login', payload);
    expect(result).toEqual(data);
  });

  it('getCurrentUser gets /auth/me and returns the unwrapped user', async () => {
    const user = { id: 1, username: 'alice', email: 'alice@example.com' };
    client.get.mockResolvedValue({ status: 200, data: { data: user } });

    const result = await getCurrentUser();

    expect(client.get).toHaveBeenCalledWith('/auth/me');
    expect(result).toEqual(user);
  });

  it('lets normalised errors propagate to callers', async () => {
    const normalised = {
      code: 'INVALID_CREDENTIALS',
      message: 'Invalid username/email or password',
      fields: {},
      status: 401,
    };
    client.post.mockRejectedValue(normalised);

    await expect(loginUser({ identifier: 'alice', password: 'nope' })).rejects.toEqual(normalised);
  });
});
