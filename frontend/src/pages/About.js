import React from 'react';
import { Container, Typography } from '@mui/material';

export default function About() {
  return (
    <div className="py-12">
      <Container maxWidth="md">
        <Typography variant="h3" component="h1" className="font-bold text-slate-900 mb-6">
          About This Application
        </Typography>
        <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 space-y-4 text-slate-700">
          <p>
            This project is built following a rigorous professional full-stack architecture. It brings together modern frontend responsiveness and backend scalability.
          </p>
          <h3 className="text-xl font-bold text-slate-900 pt-4">Technology Stack Overview</h3>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Frontend:</strong> React 19, Material UI v6, Tailwind CSS v3, React Router DOM v6, Axios.</li>
            <li><strong>Backend:</strong> Flask 3.11 REST API, Flask-JWT-Extended, Flask-Bcrypt.</li>
            <li><strong>Database:</strong> PostgreSQL 16 managed with SQLAlchemy ORM and Flask-Migrate.</li>
          </ul>
          <p className="pt-4">
            Designed with strict separation of concerns, secure authentication flows, and clean maintainable code standards.
          </p>
        </div>
      </Container>
    </div>
  );
}
