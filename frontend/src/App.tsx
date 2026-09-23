import React from 'react';
import { Typography, Container, Box, Button } from '@mui/material';

export default function App() {
  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 4, textAlign: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          React 19 + Tailwind + MUI Monorepo
        </Typography>
        <Button variant="contained" color="primary">
          Foundation Ready
        </Button>
      </Box>
    </Container>
  );
}
