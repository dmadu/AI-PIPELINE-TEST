import { Link as RouterLink } from 'react-router-dom';
import { Box, Button, Container, Paper, Stack, Typography } from '@mui/material';
import LoginForm from '../components/LoginForm';

function Home() {
  return (
    <Container maxWidth="lg" className="py-8">
      <Box className="grid grid-cols-1 gap-8 md:grid-cols-2 md:items-start">
        <Box className="flex flex-col justify-center">
          <Typography variant="h3" component="h1" className="!font-bold">
            Welcome
          </Typography>
          <Typography variant="body1" className="!mt-4 text-gray-700">
            This is the public home page. Sign in with your username or email address to reach
            your dashboard, or create a new account in a few seconds.
          </Typography>

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            className="!mt-6 w-full sm:w-auto"
          >
            <Button
              component={RouterLink}
              to="/register"
              variant="contained"
              color="secondary"
              size="large"
              className="!normal-case"
            >
              Create an account
            </Button>
            <Button
              component={RouterLink}
              to="/about"
              variant="outlined"
              size="large"
              className="!normal-case"
            >
              Learn more
            </Button>
          </Stack>

          <Typography variant="body2" className="!mt-4 text-gray-600">
            New here? Use the registration link above to sign up.
          </Typography>
        </Box>

        <Paper elevation={3} className="w-full p-6 md:p-8">
          <LoginForm />
        </Paper>
      </Box>
    </Container>
  );
}

export default Home;
