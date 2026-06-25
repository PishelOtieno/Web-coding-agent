# Coding Agent - Full Stack Application

A production-ready web application that combines an AI-powered coding assistant with a modern code editor and project management system.

## Architecture Overview

### Backend (Django)
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL 15
- **Real-time Communication**: Django Channels + Redis
- **Authentication**: JWT (SimpleJWT)
- **LLM Integration**: OpenAI API with abstraction layer for easy provider switching

**Apps**:
- `accounts`: User authentication and profile management
- `projects`: Project CRUD operations and collaboration
- `files`: File management with versioning
- `conversations`: AI conversation history
- `agents`: AI agent configuration and execution
- `tasks`: Task tracking for agent actions

### Frontend (Next.js 16)
- **Framework**: Next.js 16 with React 19
- **State Management**: Zustand
- **Data Fetching**: SWR + React Query
- **Code Editor**: Monaco Editor
- **Styling**: Tailwind CSS v4 + shadcn/ui
- **API Client**: Axios with JWT interceptors

## Project Structure

```
/vercel/share/v0-project/
├── backend/
│   ├── config/                 # Django configuration
│   ├── accounts/               # User management
│   ├── projects/               # Project management
│   ├── files/                  # File system
│   ├── conversations/          # Chat and conversations
│   ├── agents/                 # AI agent logic
│   ├── tasks/                  # Task tracking
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
├── app/                        # Next.js app directory
│   ├── login/
│   ├── register/
│   ├── dashboard/
│   └── projects/[projectId]/
├── lib/
│   ├── api-client.ts          # API integration
│   ├── auth-store.ts          # Authentication state
│   └── project-store.ts       # Project state
├── components/
│   └── protected-route.tsx    # Route protection
├── docker-compose.yml
└── package.json
```

## Getting Started

### Prerequisites
- Node.js 18+
- Docker & Docker Compose
- Python 3.11
- PostgreSQL (via Docker)
- Redis (via Docker)

### Backend Setup

1. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Run migrations**:
```bash
python manage.py migrate
```

3. **Create a superuser**:
```bash
python manage.py createsuperuser
```

4. **Set environment variables** (create `.env`):
```
DEBUG=True
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
DB_HOST=localhost
DB_NAME=coding_agent
DB_USER=postgres
DB_PASSWORD=postgres
```

5. **Run the development server**:
```bash
python manage.py runserver
```

### Frontend Setup

1. **Install dependencies**:
```bash
pnpm install
```

2. **Set environment variables** (create `.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. **Run the development server**:
```bash
pnpm dev
```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

## Key Features

### 1. Authentication
- User registration and login with JWT
- Secure token refresh mechanism
- Protected routes on frontend

### 2. Project Management
- Create, read, update, delete projects
- Organize projects by language and tags
- Collaboration features with role-based access

### 3. File Management
- Browse and edit files with Monaco Editor
- Syntax highlighting for multiple languages
- File versioning and history
- Create, update, delete files

### 4. AI Assistant
- Real-time chat with AI agent
- Context-aware code generation
- File analysis and suggestions
- Task tracking for agent actions

### 5. Code Editor
- Monaco Editor integration
- Multiple language support
- Real-time syntax highlighting
- Built-in terminal placeholder

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/auth/me/` - Get current user
- `PUT /api/auth/profile/update/` - Update user profile

### Projects
- `GET /api/projects/` - List user projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Files
- `GET /api/files/projects/{projectId}/files/` - List files
- `GET /api/files/projects/{projectId}/files/tree/` - File tree
- `POST /api/files/projects/{projectId}/files/` - Create file
- `GET /api/files/projects/{projectId}/files/{fileId}/` - Get file
- `PUT /api/files/projects/{projectId}/files/{fileId}/` - Update file
- `GET /api/files/projects/{projectId}/files/{fileId}/versions/` - File versions

### Conversations
- `GET /api/conversations/projects/{projectId}/conversations/` - List conversations
- `POST /api/conversations/projects/{projectId}/conversations/` - Create conversation
- `POST /api/conversations/projects/{projectId}/conversations/{id}/send_message/` - Send message

### Agents
- `GET /api/agents/projects/{projectId}/agent/` - Get agent
- `POST /api/agents/projects/{projectId}/agent/` - Create agent
- `POST /api/agents/projects/{projectId}/agent/{id}/generate/` - Generate code

### Tasks
- `GET /api/tasks/projects/{projectId}/tasks/` - List tasks
- `POST /api/tasks/projects/{projectId}/tasks/` - Create task
- `POST /api/tasks/projects/{projectId}/tasks/{id}/start/` - Start task
- `POST /api/tasks/projects/{projectId}/tasks/{id}/complete/` - Complete task

## Development

### Adding a New Feature

1. **Backend**: Create model → Serializer → ViewSet → URL
2. **Frontend**: Create store → API client method → Component
3. **Testing**: Add tests for both backend and frontend

### Database Migrations

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Code Quality

```bash
# Backend linting
flake8 backend/

# Frontend linting
pnpm lint
```

## Deployment

### Backend (Gunicorn + Daphne)
```bash
# Production with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Production with Daphne (for WebSocket support)
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### Frontend (Vercel)
```bash
# Build
pnpm build

# Deploy to Vercel
vercel deploy
```

## Environment Variables

### Backend (.env)
- `DEBUG`: Enable debug mode
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: OpenAI model (default: gpt-4)

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL

## LLM Integration

### Current Providers
- OpenAI (GPT-4 recommended)
- Anthropic Claude (abstraction layer ready)

### Adding a New Provider
1. Create a new class extending `BaseLLMProvider` in `backend/agents/llm_service.py`
2. Implement `generate()` and `stream()` methods
3. Register in `LLMFactory`

```python
class CustomProvider(BaseLLMProvider):
    def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        # Implementation
        pass
    
    def stream(self, messages: List[Dict[str, str]], **kwargs):
        # Implementation
        pass

LLMFactory.register_provider('custom', CustomProvider)
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose logs db

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Frontend Cannot Connect to API
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check CORS settings in Django
- Ensure backend is running on correct port

### Authentication Issues
- Clear browser localStorage
- Verify JWT secret key matches between frontend and backend
- Check token expiration settings

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

MIT

## Support

For issues and questions, open an issue on GitHub or contact the development team.
