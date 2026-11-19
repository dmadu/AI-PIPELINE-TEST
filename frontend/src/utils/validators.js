/**
 * Client-side validation helpers.
 *
 * This module MIRRORS `backend/app/utils/validators.py` and must be kept in sync
 * with it. It exists only to give users immediate, descriptive feedback; it is
 * NEVER a replacement for the authoritative server-side validation. Every rule,
 * bound, character class and message string below is a verbatim copy of the
 * backend rules so that a client-side message and the message returned by the
 * API in `error.fields` are identical for the same violation.
 *
 * Return conventions (applied uniformly):
 *  - validateEmail(value)    -> string | null  (null when valid)
 *  - validateUsername(value) -> string | null  (null when valid)
 *  - validatePassword(value) -> string[]       (empty array when valid,
 *                                               one message per failed rule,
 *                                               in a stable rule order)
 *
 * All functions are pure: no network calls, no React state, no MUI/axios imports.
 * Non-string, null and undefined inputs are treated as empty values.
 */

/* -------------------------------------------------------------------------- */
/* Shared constants (mirrors backend/app/utils/validators.py)                  */
/* -------------------------------------------------------------------------- */

/** Minimum password length enforced by the backend. */
export const PASSWORD_MIN_LENGTH = 8;

/** Username length bounds enforced by the backend. */
export const USERNAME_MIN_LENGTH = 3;
export const USERNAME_MAX_LENGTH = 50;

/** Allowed special characters for passwords (shared rule set). */
export const PASSWORD_SPECIAL_CHARACTERS = '!@#$%^&*()-_=+[]{};:,.<>?/|~';

/* Rule regexes / patterns - declared once, reused everywhere. */
const UPPERCASE_PATTERN = /[A-Z]/;
const DIGIT_PATTERN = /[0-9]/;
const SPECIAL_CHARACTER_PATTERN = /[!@#$%^&*()\-_=+[\]{};:,.<>?/|~]/;

/** Username character set: letters, digits, underscores and hyphens. */
const USERNAME_PATTERN = /^[A-Za-z0-9_-]+$/;

/**
 * Pragmatic client-side email pattern: a single `@`, a non-empty local part and
 * a domain containing a dot followed by a valid (alphabetic, 2+ chars) TLD.
 * The authoritative, RFC-compliant check is performed on the backend by the
 * `email-validator` package - this regex only catches obvious mistakes early.
 */
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[A-Za-z]{2,}$/;

/* -------------------------------------------------------------------------- */
/* Messages (copied verbatim from the backend validators)                      */
/* -------------------------------------------------------------------------- */

export const VALIDATION_MESSAGES = {
  emailRequired: 'Email is required',
  emailInvalid: 'Invalid email format',
  usernameRequired: 'Username is required',
  usernameTooShort: `Username must be at least ${USERNAME_MIN_LENGTH} characters long`,
  usernameTooLong: `Username must be at most ${USERNAME_MAX_LENGTH} characters long`,
  usernameInvalidCharacters:
    'Username may only contain letters, numbers, underscores and hyphens',
  passwordRequired: 'Password is required',
  passwordMinLength: `Password must be at least ${PASSWORD_MIN_LENGTH} characters long`,
  passwordUppercase: 'Password must contain at least one uppercase letter',
  passwordDigit: 'Password must contain at least one digit',
  passwordSpecial: `Password must contain at least one special character (${PASSWORD_SPECIAL_CHARACTERS})`,
};

/* -------------------------------------------------------------------------- */
/* Password rule set (mirrors backend PASSWORD_RULES)                          */
/* -------------------------------------------------------------------------- */

/**
 * The shared password rule set, in the stable order used by the backend.
 * Exported so forms/tests can display or iterate the rules without duplicating
 * the regexes or the message strings.
 *
 * @type {ReadonlyArray<{ name: string, message: string, test: (value: string) => boolean }>}
 */
export const PASSWORD_RULES = Object.freeze([
  Object.freeze({
    name: 'min_length',
    message: VALIDATION_MESSAGES.passwordMinLength,
    test: (value) => value.length >= PASSWORD_MIN_LENGTH,
  }),
  Object.freeze({
    name: 'uppercase',
    message: VALIDATION_MESSAGES.passwordUppercase,
    test: (value) => UPPERCASE_PATTERN.test(value),
  }),
  Object.freeze({
    name: 'digit',
    message: VALIDATION_MESSAGES.passwordDigit,
    test: (value) => DIGIT_PATTERN.test(value),
  }),
  Object.freeze({
    name: 'special',
    message: VALIDATION_MESSAGES.passwordSpecial,
    test: (value) => SPECIAL_CHARACTER_PATTERN.test(value),
  }),
]);

/* -------------------------------------------------------------------------- */
/* Helpers                                                                     */
/* -------------------------------------------------------------------------- */

/**
 * Defensively coerce any input into a string.
 * null, undefined and non-string values are treated as an empty string.
 *
 * @param {unknown} value
 * @returns {string}
 */
const toStringValue = (value) => (typeof value === 'string' ? value : '');

/* -------------------------------------------------------------------------- */
/* Validators                                                                  */
/* -------------------------------------------------------------------------- */

/**
 * Validate an email address.
 *
 * @param {unknown} value - raw field value (null/undefined/non-string => empty)
 * @returns {string|null} error message, or null when the value is valid
 */
export function validateEmail(value) {
  const email = toStringValue(value).trim();

  if (!email) {
    return VALIDATION_MESSAGES.emailRequired;
  }

  if (!EMAIL_PATTERN.test(email)) {
    return VALIDATION_MESSAGES.emailInvalid;
  }

  return null;
}

/**
 * Validate a username.
 *
 * @param {unknown} value - raw field value (null/undefined/non-string => empty)
 * @returns {string|null} error message, or null when the value is valid
 */
export function validateUsername(value) {
  const username = toStringValue(value).trim();

  if (!username) {
    return VALIDATION_MESSAGES.usernameRequired;
  }

  if (username.length < USERNAME_MIN_LENGTH) {
    return VALIDATION_MESSAGES.usernameTooShort;
  }

  if (username.length > USERNAME_MAX_LENGTH) {
    return VALIDATION_MESSAGES.usernameTooLong;
  }

  if (!USERNAME_PATTERN.test(username)) {
    return VALIDATION_MESSAGES.usernameInvalidCharacters;
  }

  return null;
}

/**
 * Validate a password against the shared password rule set.
 * Returns one message per failed rule, in the stable PASSWORD_RULES order,
 * so every violation can be shown at once.
 *
 * @param {unknown} value - raw field value (null/undefined/non-string => empty)
 * @returns {string[]} list of error messages (empty when the password is valid)
 */
export function validatePassword(value) {
  const password = toStringValue(value);

  if (!password) {
    return [VALIDATION_MESSAGES.passwordRequired];
  }

  return PASSWORD_RULES.filter((rule) => !rule.test(password)).map((rule) => rule.message);
}

export default {
  validateEmail,
  validateUsername,
  validatePassword,
  PASSWORD_RULES,
  VALIDATION_MESSAGES,
  PASSWORD_MIN_LENGTH,
  USERNAME_MIN_LENGTH,
  USERNAME_MAX_LENGTH,
  PASSWORD_SPECIAL_CHARACTERS,
};
