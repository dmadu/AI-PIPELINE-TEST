import React, { useState, useEffect } from 'react';
import { projectService } from '../services/api';
import './Projects.css';

const Projects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const data = await projectService.getProjects();
        setProjects(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch projects. Please try again later.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  if (loading) {
    return <div className="projects-loading">Loading projects...</div>;
  }

  if (error) {
    return <div className="projects-error">{error}</div>;
  }

  return (
    <div className="projects-container">
      <header className="projects-header">
        <h1>Projects</h1>
        <p>Manage and view your organization's projects.</p>
      </header>

      {projects.length === 0 ? (
        <div className="no-projects">No projects found.</div>
      ) : (
        <div className="projects-grid">
          {projects.map((project) => (
            <div key={project.id || project._id} className="project-card">
              <h3>{project.name}</h3>
              <p>{project.description}</p>
              {project.status && (
                <span className={`project-status status-${project.status.toLowerCase()}`}>
                  {project.status}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

projects.displayName = 'Projects';

export default Projects;
