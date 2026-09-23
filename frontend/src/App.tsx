import React from 'react';
import { Button, Container, Typography } from '@mui/material';

export default function App() {
  return (
    <Container className="py-10">
      <Typography variant="h4" component="h1" gutterBottom className="font-bold">
        React 19 + Tailwind + MUI Monorepo Frontend
      </Typography>
      <Button variant="contained" color="primary">
        Get Started
      </Button>
    </Container>
  );
}
