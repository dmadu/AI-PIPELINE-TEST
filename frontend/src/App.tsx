import React from 'react';
import { Button, Container, Typography } from '@mui/material';

export default function App() {
  return (
    <Container maxWidth="sm" className="py-12 text-center">
      <Typography variant="h4" component="h1" gutterBottom className="font-bold">
        Frontend Monorepo Setup
      </Typography>
      <Button variant="contained" color="primary">
        MUI Button
      </Button>
    </Container>
  );
}
