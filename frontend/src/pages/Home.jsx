import { Box, Button, Container, Divider, Paper, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const highlights = [
  {
    title: 'Secure registration',
    description:
      'Accounts are validated on the server and passwords are stored as bcrypt hashes - never in plain text.',
  },
  {
    title: 'Token based sign in',
    description:
      'Signing in issues a short lived JSON Web Token that protects every private area of the application.',
  },
  {
    title: 'Responsive by default',
    description:
      'The interface adapts from small phones to wide desktops, so you can work comfortably on any device.',
  },
];

export default function Home() {
  return (
    <Container
      maxWidth="lg"
      component="main"
      data-testid="home-page"
      className="w-full max-w-full px-4 py-8 sm:py-12"
    >
      {/* Hero / introduction */}
      <Box
        component="section"
        data-testid="home-hero"
        className="flex flex-col gap-8 lg:flex-row lg:items-start lg:gap-12"
      >
        <Stack spacing={2} className="w-full lg:w-7/12">
          <Typography variant="overline" color="primary" className="tracking-widest">
            Secure user authentication
          </Typography>

          <Typography variant="h3" component="h1" className="break-words" sx={{ fontWeight: 700 }}>
            Welcome to SecureAuth
          </Typography>

          <Typography variant="body1" color="text.secondary" className="max-w-prose">
            SecureAuth is a small, focused demonstration of a complete registration and login
            workflow: a React single page application talking to a Flask REST API backed by
            PostgreSQL. Create an account, sign in and reach your personal dashboard - with every
            rule enforced on the server.
          </Typography>

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            className="pt-2"
            alignItems={{ xs: 'stretch', sm: 'center' }}
          >
            <Button component={RouterLink} to="/about" variant="contained" size="large">
              Learn more about us
            </Button>
            <Button component={RouterLink} to="/contact" variant="outlined" size="large">
              Contact us
            </Button>
          </Stack>
        </Stack>

        {/* ----------------------------------------------------------------- */}
        {/* Auth slot: LoginForm + Register link - Phase 4                      */}
        {/* Replace the contents of this Paper with <LoginForm /> and the       */}
        {/* registration link. No form or auth logic lives here yet.            */}
        {/* ----------------------------------------------------------------- */}
        <Paper
          variant="outlined"
          data-testid="home-auth-slot"
          aria-label="Sign in area placeholder"
          className="w-full p-6 lg:w-5/12"
          sx={{ borderStyle: 'dashed', borderWidth: 2 }}
        >
          <Stack spacing={1.5}>
            <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
              Sign in
            </Typography>
            <Divider />
            <Typography variant="body2" color="text.secondary">
              This area is reserved for the login form and the link used to create a new account.
              Both arrive in the next development phase.
            </Typography>
            <Typography variant="caption" color="text.disabled">
              Placeholder only - no form fields or authentication logic are implemented yet.
            </Typography>
          </Stack>
        </Paper>
      </Box>

      <Divider className="!my-10" />

      {/* Highlights */}
      <Box component="section" data-testid="home-highlights">
        <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }} className="mb-4">
          What you get
        </Typography>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {highlights.map((item) => (
            <Paper key={item.title} elevation={1} className="h-full p-5">
              <Typography variant="subtitle1" component="h3" sx={{ fontWeight: 600 }}>
                {item.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" className="mt-2">
                {item.description}
              </Typography>
            </Paper>
          ))}
        </div>
      </Box>
    </Container>
  );
}
