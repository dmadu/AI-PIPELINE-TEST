import { Box, Button, Container, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

export default function NotFound() {
  return (
    <Container
      maxWidth="sm"
      component="main"
      data-testid="notfound-page"
      className="w-full max-w-full px-4 py-12 sm:py-20"
    >
      <Box className="flex flex-col items-center text-center">
        <Stack spacing={2} alignItems="center">
          <Typography
            variant="h2"
            component="h1"
            sx={{ fontWeight: 800, lineHeight: 1 }}
            className="break-words"
          >
            404
          </Typography>

          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            Page not found
          </Typography>

          <Typography variant="body1" color="text.secondary" className="max-w-prose">
            The page you are looking for does not exist, or it may have been moved. Check the
            address, or head back to the home page and start again.
          </Typography>

          <Button
            component={RouterLink}
            to="/"
            variant="contained"
            size="large"
            className="mt-2"
            data-testid="notfound-home-link"
          >
            Back to Home
          </Button>
        </Stack>
      </Box>
    </Container>
  );
}
