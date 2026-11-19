import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import Alert from './Alert';
import { useAuth } from '../context/AuthContext';

const INITIAL_VALUES = { identifier: '', password: '' };

/** Generic message used when the API does not provide one (never reveals user existence). */
const GENERIC_ERROR_MESSAGE = 'Invalid username/email or password';

/**
 * Normalises whatever the AuthContext / axios interceptor rejects with into the
 * error-envelope shape the shared Alert component understands.
 */
const normaliseError = (err) => {
  const source = (err && err.error && typeof err.error === 'object' ? err.error : err) || {};

  if (typeof source === 'string') {
    return { message: source };
  }

  return {
    code: source.code,
    message: source.message || GENERIC_ERROR_MESSAGE,
    fields: source.fields,
  };
};

function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [values, setValues] = useState(INITIAL_VALUES);
  const [fieldErrors, setFieldErrors] = useState({});
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setValues((previous) => ({ ...previous, [name]: value }));
    setFieldErrors((previous) => {
      if (!previous[name]) {
        return previous;
      }
      const next = { ...previous };
      delete next[name];
      return next;
    });
  };

  // Login only checks that both fields are present; password rules stay server-side.
  const validate = () => {
    const errors = {};
    if (!values.identifier.trim()) {
      errors.identifier = 'Username or email is required';
    }
    if (!values.password.trim()) {
      errors.password = 'Password is required';
    }
    return errors;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);

    const errors = validate();
    setFieldErrors(errors);
    if (Object.keys(errors).length > 0) {
      return;
    }

    setSubmitting(true);
    try {
      const result = await login({
        identifier: values.identifier.trim(),
        password: values.password,
      });

      if (result && result.success === false) {
        throw result.error || new Error(GENERIC_ERROR_MESSAGE);
      }

      navigate('/dashboard', { replace: true });
    } catch (err) {
      const normalised = normaliseError(err);
      setError(normalised);
      if (normalised.fields && typeof normalised.fields === 'object') {
        setFieldErrors(normalised.fields);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      aria-label="Login form"
      className="w-full"
    >
      <Typography variant="h5" component="h2" className="!mb-1 !font-semibold">
        Log in
      </Typography>
      <Typography variant="body2" className="!mb-4 text-gray-600">
        Use your username or email address with your password.
      </Typography>

      {error ? (
        <div className="mb-4">
          <Alert error={error} severity="error" />
        </div>
      ) : null}

      <Stack spacing={2} className="w-full">
        <TextField
          id="login-identifier"
          name="identifier"
          label="Username or Email"
          value={values.identifier}
          onChange={handleChange}
          error={Boolean(fieldErrors.identifier)}
          helperText={fieldErrors.identifier || ' '}
          autoComplete="username"
          fullWidth
          disabled={submitting}
        />

        <TextField
          id="login-password"
          name="password"
          label="Password"
          type="password"
          value={values.password}
          onChange={handleChange}
          error={Boolean(fieldErrors.password)}
          helperText={fieldErrors.password || ' '}
          autoComplete="current-password"
          fullWidth
          disabled={submitting}
        />

        <Button
          type="submit"
          variant="contained"
          color="primary"
          size="large"
          fullWidth
          disabled={submitting}
          startIcon={submitting ? <CircularProgress size={18} color="inherit" /> : null}
          className="!normal-case"
        >
          Sign In
        </Button>
      </Stack>
    </Box>
  );
}

export default LoginForm;
