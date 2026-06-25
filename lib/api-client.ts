import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadTokensFromStorage();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          if (this.refreshToken) {
            try {
              const response = await this.refreshTokens();
              this.setTokens(response.data.access, response.data.refresh || this.refreshToken);
              return this.client(originalRequest);
            } catch (refreshError) {
              this.clearTokens();
              if (typeof window !== 'undefined') {
                window.location.href = '/login';
              }
              return Promise.reject(refreshError);
            }
          }
        }

        return Promise.reject(error);
      }
    );
  }

  private loadTokensFromStorage() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('accessToken');
      this.refreshToken = localStorage.getItem('refreshToken');
    }
  }

  private setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    if (typeof window !== 'undefined') {
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
    }
  }

  private clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  }

  async refreshTokens() {
    return this.client.post('/auth/refresh/', { refresh: this.refreshToken });
  }

  // Auth endpoints
  async register(username: string, email: string, password: string, password2: string) {
    return this.client.post('/auth/register/', {
      username,
      email,
      password,
      password2,
    });
  }

  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login/', { username, password });
    this.setTokens(response.data.access, response.data.refresh);
    return response;
  }

  async logout() {
    this.clearTokens();
  }

  async getCurrentUser() {
    return this.client.get('/auth/me/');
  }

  async updateProfile(data: any) {
    return this.client.put('/auth/profile/update/', data);
  }

  // Projects endpoints
  async getProjects() {
    return this.client.get('/projects/');
  }

  async getProject(id: number) {
    return this.client.get(`/projects/${id}/`);
  }

  async createProject(data: any) {
    return this.client.post('/projects/', data);
  }

  async updateProject(id: number, data: any) {
    return this.client.put(`/projects/${id}/`, data);
  }

  async deleteProject(id: number) {
    return this.client.delete(`/projects/${id}/`);
  }

  // Files endpoints
  async getFiles(projectId: number) {
    return this.client.get(`/files/projects/${projectId}/files/`);
  }

  async getFileTree(projectId: number) {
    return this.client.get(`/files/projects/${projectId}/files/tree/`);
  }

  async getFile(projectId: number, fileId: number) {
    return this.client.get(`/files/projects/${projectId}/files/${fileId}/`);
  }

  async createFile(projectId: number, data: any) {
    return this.client.post(`/files/projects/${projectId}/files/`, data);
  }

  async updateFile(projectId: number, fileId: number, data: any) {
    return this.client.put(`/files/projects/${projectId}/files/${fileId}/`, data);
  }

  async deleteFile(projectId: number, fileId: number) {
    return this.client.delete(`/files/projects/${projectId}/files/${fileId}/`);
  }

  async getFileVersions(projectId: number, fileId: number) {
    return this.client.get(`/files/projects/${projectId}/files/${fileId}/versions/`);
  }

  // Conversations endpoints
  async getConversations(projectId: number) {
    return this.client.get(`/conversations/projects/${projectId}/conversations/`);
  }

  async getConversation(projectId: number, conversationId: number) {
    return this.client.get(`/conversations/projects/${projectId}/conversations/${conversationId}/`);
  }

  async createConversation(projectId: number, data: any) {
    return this.client.post(`/conversations/projects/${projectId}/conversations/`, data);
  }

  async sendMessage(projectId: number, conversationId: number, content: string) {
    return this.client.post(`/conversations/projects/${projectId}/conversations/${conversationId}/send_message/`, {
      content,
    });
  }

  async getMessages(projectId: number, conversationId: number) {
    const response = await this.getConversation(projectId, conversationId);
    return response.data.messages || [];
  }

  // Agents endpoints
  async getAgent(projectId: number) {
    return this.client.get(`/agents/projects/${projectId}/agent/`);
  }

  async createAgent(projectId: number, data: any) {
    return this.client.post(`/agents/projects/${projectId}/agent/`, data);
  }

  async generateCode(projectId: number, agentId: number, prompt: string) {
    return this.client.post(`/agents/projects/${projectId}/agent/${agentId}/generate/`, {
      prompt,
    });
  }

  // Tasks endpoints
  async getTasks(projectId: number) {
    return this.client.get(`/tasks/projects/${projectId}/tasks/`);
  }

  async getTask(projectId: number, taskId: number) {
    return this.client.get(`/tasks/projects/${projectId}/tasks/${taskId}/`);
  }

  async createTask(projectId: number, data: any) {
    return this.client.post(`/tasks/projects/${projectId}/tasks/`, data);
  }

  async startTask(projectId: number, taskId: number) {
    return this.client.post(`/tasks/projects/${projectId}/tasks/${taskId}/start/`, {});
  }

  async completeTask(projectId: number, taskId: number, result: any) {
    return this.client.post(`/tasks/projects/${projectId}/tasks/${taskId}/complete/`, { result });
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }
}

export const apiClient = new ApiClient();
