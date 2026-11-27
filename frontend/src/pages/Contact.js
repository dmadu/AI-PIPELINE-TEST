import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Alert } from '@mui/material';

export default function Contact() {
  const [submitted, setSubmitted] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', message: '' });

  const handleSubmit = (e) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="py-12">
      <Container maxWidth="md">
        <Typography variant="h3" component="h1" className="font-bold text-slate-900 mb-6">
          Contact Us
        </Typography>
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200">
          {submitted ? (
            <Alert severity="success" className="mb-4">
              Thank you for your message! We will get back to you soon.
            </Alert>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <TextField
                fullWidth
                label="Name"
                variant="outlined"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
              <TextField
                fullWidth
                label="Email"
                type="email"
                variant="outlined"
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              <TextField
                fullWidth
                label="Message"
                multiline
                rows={4}
                variant="outlined"
                required
                value={form.message}
                onChange={(e) => setForm({ ...form, message: e.target.value })}
              />
              <Button type="submit" variant="contained" size="large" sx={{ bgcolor: '#4f46e5', '&:hover': { bgcolor: '#4338ca' } }}>
                Send Message
              </Button>
            </form>
          )}
        </div>
      </Container>
    </div>
  );
}
