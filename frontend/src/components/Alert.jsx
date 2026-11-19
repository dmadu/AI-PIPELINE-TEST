import { Alert as MuiAlert, AlertTitle } from '@mui/material';

/**
 * Reusable presentational wrapper around MUI's Alert used to render the API
 * error envelope ({ code, message, fields }) consistently across forms.
 *
 * Renders nothing when there is neither a message nor any field error.
 *
 * @param {object} props
 * @param {string} [props.message] main (human readable) API message
 * @param {Object<string, string|string[]>} [props.fields] field -> message map
 * @param {'error'|'warning'|'info'|'success'} [props.severity='error']
 * @param {string} [props.title] optional alert title
 * @param {Function} [props.onClose] when supplied, a close button is rendered
 * @param {string} [props.className] extra Tailwind classes
 */
function Alert({
  message = '',
  fields = null,
  severity = 'error',
  title = '',
  onClose = undefined,
  className = '',
}) {
  const fieldEntries = fields
    ? Object.entries(fields).filter(([, value]) => Boolean(value))
    : [];

  if (!message && fieldEntries.length === 0) {
    return null;
  }

  return (
    <MuiAlert
      severity={severity}
      onClose={onClose}
      className={`w-full my-2 ${className}`.trim()}
    >
      {title ? <AlertTitle>{title}</AlertTitle> : null}
      {message ? <span className="block">{message}</span> : null}
      {fieldEntries.length > 0 ? (
        <ul className="mt-1 mb-0 pl-5 list-disc">
          {fieldEntries.map(([field, value]) => (
            <li key={field} className="text-sm">
              <strong>{field}</strong>: {Array.isArray(value) ? value.join(', ') : value}
            </li>
          ))}
        </ul>
      ) : null}
    </MuiAlert>
  );
}

export default Alert;
