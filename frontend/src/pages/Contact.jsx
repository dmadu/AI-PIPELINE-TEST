import { Container, Divider, Paper, Stack, Typography } from '@mui/material';

const contactDetails = [
  { label: 'Email', value: 'support@secureauth.example' },
  { label: 'Phone', value: '+1 (555) 014-7788' },
  { label: 'Address', value: '42 Example Avenue, Suite 300, Springfield, 11000' },
  { label: 'Office hours', value: 'Monday to Friday, 09:00 - 17:00 (UTC)' },
];

export default function Contact() {
  return (
    <Container
      maxWidth="md"
      component="main"
      data-testid="contact-page"
      className="w-full max-w-full px-4 py-8 sm:py-12"
    >
      <Stack spacing={2} className="max-w-2xl">
        <Typography variant="h3" component="h1" sx={{ fontWeight: 700 }} className="break-words">
          Contact Us
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Questions about SecureAuth, an account issue or feedback on the project? Use any of the
          details below and a member of the team will get back to you.
        </Typography>
      </Stack>

      <Divider className="!my-8" />

      <Paper elevation={1} className="p-5 sm:p-6" data-testid="contact-details">
        <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }} className="mb-4">
          Contact details
        </Typography>

        <Stack spacing={2} divider={<Divider flexItem />}>
          {contactDetails.map((detail) => (
            <Stack
              key={detail.label}
              direction={{ xs: 'column', sm: 'row' }}
              spacing={{ xs: 0.5, sm: 2 }}
              alignItems={{ xs: 'flex-start', sm: 'center' }}
            >
              <Typography
                variant="subtitle2"
                component="h3"
                color="text.secondary"
                sx={{ minWidth: 140 }}
              >
                {detail.label}
              </Typography>
              <Typography variant="body1" className="break-words">
                {detail.value}
              </Typography>
            </Stack>
          ))}
        </Stack>
      </Paper>

      <Typography variant="caption" color="text.disabled" className="mt-4 block">
        These details are provided for demonstration purposes only.
      </Typography>
    </Container>
  );
}
