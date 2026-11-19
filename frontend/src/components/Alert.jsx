import { Alert as MuiAlert, AlertTitle, Box } from '@mui/material';

/**
 * Accepts either a plain message, a string error, or the normalised API error
 * envelope ({ code, message, fields }) - or the raw { error: {...} } payload.
 */
const resolveError = (error) => {
  if (!error) {
    return {};
  }
  if (typeof error === 'string') {
    return { message: error };
  }
  if (error.error && typeof error.error === 'object') {
    return error.error;
  }
  return error;
};

function Alert({
  error = null,
  message = '',
  fields = null,
  severity = 'error',
  title = '',
  onClose = null,
  className = '',
  children = null,
}) {
  const resolved = resolveError(error);
  const text = message || resolved.message || '';
  const fieldErrors = fields || resolved.fields || null;

  const entries =
    fieldErrors && typeof fieldErrors === 'object'
      ? Object.entries(fieldErrors).filter(([, value]) => Boolean(value))
      : [];

  if (!text && entries.length === 0 && !children) {
    return null;
  }

  return (
    <MuiAlert
      severity={severity}
      onClose={onClose || undefined}
      className={`w-full ${className}`.trim()}
    >
      {title ? <AlertTitle>{title}</AlertTitle> : null}
      {text}
      {entries.length > 0 ? (
        <Box component="ul" className="mt-1 list-disc pl-5">
          {entries.map(([field, value]) => (
            <Box component="li" key={field}>
              {Array.isArray(value) ? value.join(' ') : value}
            </Box>
          ))}
        </Box>
      ) : null}
      {children}
    </MuiAlert>
  );
}

export default Alert;
