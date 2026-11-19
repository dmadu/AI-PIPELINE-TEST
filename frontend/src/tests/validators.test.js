import { describe, it, expect } from 'vitest';

import {
  validateEmail,
  validateUsername,
  validatePassword,
  PASSWORD_RULES,
  PASSWORD_MIN_LENGTH,
  USERNAME_MIN_LENGTH,
  USERNAME_MAX_LENGTH,
  PASSWORD_SPECIAL_CHARACTERS,
} from '../utils/validators';

/**
 * Expected messages are hardcoded here (copies of the strings in
 * backend/app/utils/validators.py) so that any drift between the backend rules
 * and the mirrored frontend rules is caught by this spec.
 */
const BACKEND_MESSAGES = {
  emailRequired: 'Email is required',
  emailInvalid: 'Invalid email format',
  usernameRequired: 'Username is required',
  usernameTooShort: 'Username must be at least 3 characters long',
  usernameTooLong: 'Username must be at most 50 characters long',
  usernameInvalidCharacters:
    'Username may only contain letters, numbers, underscores and hyphens',
  passwordRequired: 'Password is required',
  passwordMinLength: 'Password must be at least 8 characters long',
  passwordUppercase: 'Password must contain at least one uppercase letter',
  passwordDigit: 'Password must contain at least one digit',
  passwordSpecial:
    'Password must contain at least one special character (!@#$%^&*()-_=+[]{};:,.<>?/|~)',
};

describe('shared validation constants', () => {
  it('mirrors the backend bounds and special character set', () => {
    expect(PASSWORD_MIN_LENGTH).toBe(8);
    expect(USERNAME_MIN_LENGTH).toBe(3);
    expect(USERNAME_MAX_LENGTH).toBe(50);
    expect(PASSWORD_SPECIAL_CHARACTERS).toBe('!@#$%^&*()-_=+[]{};:,.<>?/|~');
  });

  it('exposes the password rules in a stable order with backend messages', () => {
    expect(PASSWORD_RULES.map((rule) => rule.name)).toEqual([
      'min_length',
      'uppercase',
      'digit',
      'special',
    ]);
    expect(PASSWORD_RULES.map((rule) => rule.message)).toEqual([
      BACKEND_MESSAGES.passwordMinLength,
      BACKEND_MESSAGES.passwordUppercase,
      BACKEND_MESSAGES.passwordDigit,
      BACKEND_MESSAGES.passwordSpecial,
    ]);
  });
});

describe('validateEmail', () => {
  it.each([
    'user@example.com',
    'first.last@example.co.uk',
    'user+tag@sub.example.org',
    'USER@EXAMPLE.COM',
  ])('accepts the valid address %s', (email) => {
    expect(validateEmail(email)).toBeNull();
  });

  it('trims surrounding whitespace before validating', () => {
    expect(validateEmail('  user@example.com  ')).toBeNull();
  });

  it('rejects empty values', () => {
    expect(validateEmail('')).toBe(BACKEND_MESSAGES.emailRequired);
    expect(validateEmail('   ')).toBe(BACKEND_MESSAGES.emailRequired);
  });

  it.each([
    'userexample.com',
    'user@@example.com',
    'user@',
    '@example.com',
    'user@example',
    'user@example.',
    'user name@example.com',
  ])('rejects the malformed address %s', (email) => {
    expect(validateEmail(email)).toBe(BACKEND_MESSAGES.emailInvalid);
  });

  it('treats null, undefined and non-string input as empty', () => {
    expect(validateEmail(null)).toBe(BACKEND_MESSAGES.emailRequired);
    expect(validateEmail(undefined)).toBe(BACKEND_MESSAGES.emailRequired);
    expect(validateEmail(42)).toBe(BACKEND_MESSAGES.emailRequired);
    expect(validateEmail({})).toBe(BACKEND_MESSAGES.emailRequired);
    expect(validateEmail([])).toBe(BACKEND_MESSAGES.emailRequired);
  });
});

describe('validateUsername', () => {
  it.each(['abc', 'john_doe', 'jane-doe99', 'A'.repeat(USERNAME_MAX_LENGTH)])(
    'accepts the valid username %s',
    (username) => {
      expect(validateUsername(username)).toBeNull();
    },
  );

  it('rejects empty values', () => {
    expect(validateUsername('')).toBe(BACKEND_MESSAGES.usernameRequired);
    expect(validateUsername('   ')).toBe(BACKEND_MESSAGES.usernameRequired);
  });

  it('rejects usernames that are too short', () => {
    expect(validateUsername('ab')).toBe(BACKEND_MESSAGES.usernameTooShort);
  });

  it('rejects usernames that are too long', () => {
    expect(validateUsername('a'.repeat(USERNAME_MAX_LENGTH + 1))).toBe(
      BACKEND_MESSAGES.usernameTooLong,
    );
  });

  it.each(['john doe', 'john.doe', 'john@doe', 'john#doe'])(
    'rejects the disallowed characters in %s',
    (username) => {
      expect(validateUsername(username)).toBe(BACKEND_MESSAGES.usernameInvalidCharacters);
    },
  );

  it('treats null, undefined and non-string input as empty', () => {
    expect(validateUsername(null)).toBe(BACKEND_MESSAGES.usernameRequired);
    expect(validateUsername(undefined)).toBe(BACKEND_MESSAGES.usernameRequired);
    expect(validateUsername(1234)).toBe(BACKEND_MESSAGES.usernameRequired);
    expect(validateUsername({})).toBe(BACKEND_MESSAGES.usernameRequired);
  });
});

describe('validatePassword', () => {
  it('returns no errors for a compliant password', () => {
    expect(validatePassword('Str0ng!Pass')).toEqual([]);
  });

  it('returns the required message for empty values', () => {
    expect(validatePassword('')).toEqual([BACKEND_MESSAGES.passwordRequired]);
  });

  it('returns exactly one message when a single rule fails', () => {
    expect(validatePassword('str0ng!pass')).toEqual([BACKEND_MESSAGES.passwordUppercase]);
    expect(validatePassword('Strong!pass')).toEqual([BACKEND_MESSAGES.passwordDigit]);
    expect(validatePassword('Str0ngpass')).toEqual([BACKEND_MESSAGES.passwordSpecial]);
    expect(validatePassword('Str0ng!')).toEqual([BACKEND_MESSAGES.passwordMinLength]);
  });

  it('returns one message per failed rule in a stable order', () => {
    expect(validatePassword('abc')).toEqual([
      BACKEND_MESSAGES.passwordMinLength,
      BACKEND_MESSAGES.passwordUppercase,
      BACKEND_MESSAGES.passwordDigit,
      BACKEND_MESSAGES.passwordSpecial,
    ]);

    expect(validatePassword('abcdefgh1')).toEqual([
      BACKEND_MESSAGES.passwordUppercase,
      BACKEND_MESSAGES.passwordSpecial,
    ]);
  });

  it('accepts every special character from the shared rule set', () => {
    PASSWORD_SPECIAL_CHARACTERS.split('').forEach((character) => {
      expect(validatePassword(`Abcdefg1${character}`)).toEqual([]);
    });
  });

  it('does not trim passwords', () => {
    expect(validatePassword('   ')).toEqual([
      BACKEND_MESSAGES.passwordMinLength,
      BACKEND_MESSAGES.passwordUppercase,
      BACKEND_MESSAGES.passwordDigit,
      BACKEND_MESSAGES.passwordSpecial,
    ]);
  });

  it('treats null, undefined and non-string input as empty', () => {
    expect(validatePassword(null)).toEqual([BACKEND_MESSAGES.passwordRequired]);
    expect(validatePassword(undefined)).toEqual([BACKEND_MESSAGES.passwordRequired]);
    expect(validatePassword(12345678)).toEqual([BACKEND_MESSAGES.passwordRequired]);
    expect(validatePassword({})).toEqual([BACKEND_MESSAGES.passwordRequired]);
  });
});
