'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth-store';
import { useProjectStore, Project } from '@/lib/project-store';
import { ProtectedRoute } from '@/components/protected-route';
import { Button } from '@/components/ui/button';

function ProjectCard({ project }: { project: Project }) {
  return (
    <Link href={`/projects/${project.id}`}>
      <div className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition cursor-pointer group">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition">
              {project.name}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">{project.description || 'No description'}</p>
          </div>
          <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-medium">
            {project.language}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            {project.tags?.map((tag) => (
              <span key={tag} className="bg-muted text-muted-foreground px-2 py-1 rounded text-xs">
                {tag}
              </span>
            ))}
          </div>
          <span className="text-xs text-muted-foreground">
            {new Date(project.updated_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </Link>
  );
}

function DashboardContent() {
  const { user, logout } = useAuthStore();
  const { projects, isLoading, fetchProjects } = useProjectStore();
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    language: 'python',
  });

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleCreateProject = async () => {
    if (!newProject.name.trim()) return;
    
    try {
      await useProjectStore.getState().createProject(newProject);
      setNewProject({ name: '', description: '', language: 'python' });
      setShowNewProject(false);
      fetchProjects();
    } catch (error) {
      console.error('Failed to create project:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">Coding Agent</h1>
            <p className="text-sm text-muted-foreground">Welcome back, {user?.username}</p>
          </div>
          <Button
            onClick={logout}
            variant="outline"
            className="border-border text-foreground hover:bg-muted"
          >
            Sign Out
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Section Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-foreground">Your Projects</h2>
            <p className="text-muted-foreground mt-1">Manage and organize your coding projects</p>
          </div>
          <Button
            onClick={() => setShowNewProject(!showNewProject)}
            className="bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            {showNewProject ? 'Cancel' : 'New Project'}
          </Button>
        </div>

        {/* New Project Form */}
        {showNewProject && (
          <div className="bg-card border border-border rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-foreground mb-4">Create a New Project</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Project Name</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="My Awesome Project"
                  className="w-full px-4 py-2 bg-background border border-border rounded-md focus:ring-2 focus:ring-primary text-foreground placeholder-muted-foreground"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="Describe your project..."
                  rows={3}
                  className="w-full px-4 py-2 bg-background border border-border rounded-md focus:ring-2 focus:ring-primary text-foreground placeholder-muted-foreground"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Language</label>
                <select
                  value={newProject.language}
                  onChange={(e) => setNewProject({ ...newProject, language: e.target.value })}
                  className="w-full px-4 py-2 bg-background border border-border rounded-md focus:ring-2 focus:ring-primary text-foreground"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <Button
                onClick={handleCreateProject}
                className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
              >
                Create Project
              </Button>
            </div>
          </div>
        )}

        {/* Projects Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-foreground">Loading projects...</p>
            </div>
          </div>
        ) : projects.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">No projects yet. Create your first project to get started!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
