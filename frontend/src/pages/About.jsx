import { Box, Container, Divider, Paper, Stack, Typography } from '@mui/material';

const sections = [
  {
    title: 'Our mission',
    body:
      'We believe secure authentication should be approachable. SecureAuth shows how a modern single page application and a well structured REST API can cooperate to keep user credentials safe without making the experience complicated.',
  },
  {
    title: 'How it works',
    body:
      'The React frontend handles navigation and immediate feedback, while the Flask API performs the authoritative validation, hashes passwords with bcrypt and issues short lived JSON Web Tokens. User records live in PostgreSQL and schema changes are managed with migrations.',
  },
  {
    title: 'Our approach',
    body:
      'Small, well tested building blocks: a shared layout, reusable form components, a single configured HTTP client and clear error envelopes. Every rule enforced in the browser is mirrored on the server, never replaced by it.',
  },
];

const team = [
  { name: 'Product', role: 'Defines the user journeys and keeps the scope focused.' },
  { name: 'Engineering', role: 'Builds the React frontend, the Flask API and the data layer.' },
  { name: 'Quality', role: 'Owns the automated test suites for both services.' },
];

export default function About() {
  return (
    <Container
      maxWidth="lg"
      component="main"
      data-testid="about-page"
      className="w-full max-w-full px-4 py-8 sm:py-12"
    >
      <Stack spacing={2} className="max-w-3xl">
        <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }} className="break-words">
          About Us
        </Typography>
        <Typography variant="body1" color="text.secondary">
          SecureAuth is a reference application for user registration, login and protected content.
          It is deliberately small so that every moving part stays easy to read, review and reuse.
        </Typography>
      </Stack>

      <Divider className="!my-8" />

      <Box component="section" className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {sections.map((section) => (
          <Paper key={section.title} elevation={1} className="h-full p-5">
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
              {section.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" className="mt-2">
              {section.body}
            </Typography>
          </Paper>
        ))}
      </Box>

      <Divider className="!my-8" />

      <Box component="section" data-testid="about-team">
        <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }} className="mb-4">
          The team
        </Typography>

        <Stack spacing={2}>
          {team.map((member) => (
            <Paper key={member.name} variant="outlined" className="p-4">
              <Stack
                direction={{ xs: 'column', sm: 'row' }}
                spacing={{ xs: 0.5, sm: 2 }}
                alignItems={{ xs: 'flex-start', sm: 'center' }}
              >
                <Typography
                  variant="subtitle1"
                  component="h3"
                  sx={{ fontWeight: 600, minWidth: 140 }}
                >
                  {member.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {member.role}
                </Typography>
              </Stack>
            </Paper>
          ))}
        </Stack>
      </Box>
    </Container>
  );
}
