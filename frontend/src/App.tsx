import React from 'react';
import { Typography, Container, Box } from '@mui/material';

export default function App() {
  return (
    <Container maxWidth="sm">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom className="text-blue-600 font-bold">
          React 19 + TypeScript + Tailwind + MUI
        </Typography>
      </Box>
    </Container>
  );
}
