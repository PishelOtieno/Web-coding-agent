'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useProjectStore } from '@/lib/project-store';
import { apiClient } from '@/lib/api-client';
import { ProtectedRoute } from '@/components/protected-route';
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('@monaco-editor/react').then((mod) => mod.default), {
  ssr: false,
});

interface File {
  id: number;
  name: string;
  path: string;
  content?: string;
  language?: string;
}

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
}

interface Conversation {
  id: number;
  title: string;
  messages?: Message[];
}

function WorkspaceContent() {
  const params = useParams();
  const projectId = Number(params.projectId);
  const { currentProject, fetchProject } = useProjectStore();
  
  const [files, setFiles] = useState<File[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSavingFile, setIsSavingFile] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);
  const [chatError, setChatError] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);
  const [showTerminal, setShowTerminal] = useState(false);

  useEffect(() => {
    fetchProject(projectId);
    loadFiles();
    loadConversations();
  }, [projectId]);

  const loadFiles = async () => {
    try {
      setFileError(null);
      const response = await apiClient.getFileTree(projectId);
      const nextFiles = response.data || [];
      setFiles(nextFiles);
      if (nextFiles.length > 0) {
        await selectFile(nextFiles[0]);
      }
    } catch (error) {
      console.error('Failed to load files:', error);
      setFileError('Failed to load files.');
    }
  };

  const loadConversations = async () => {
    try {
      setChatError(null);
      const response = await apiClient.getConversations(projectId);
      let nextConversations = response.data?.results || response.data || [];
      if (nextConversations.length === 0) {
        const created = await apiClient.createConversation(projectId, {
          title: 'Project Assistant',
          description: 'Default project support conversation',
        });
        nextConversations = [created.data];
      }
      setConversations(nextConversations);
      setMessages(nextConversations[0]?.messages || []);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      setChatError('Failed to load assistant conversation.');
    }
  };

  const selectFile = async (file: File) => {
    try {
      setFileError(null);
      const response = await apiClient.getFile(projectId, file.id);
      setSelectedFile(response.data);
      setIsDirty(false);
    } catch (error) {
      console.error('Failed to load file:', error);
      setFileError('Failed to load file content.');
    }
  };

  const handleSaveFile = async () => {
    if (!selectedFile) return;

    setIsSavingFile(true);
    setFileError(null);
    try {
      const content = selectedFile.content || '';
      const response = await apiClient.updateFile(projectId, selectedFile.id, {
        ...selectedFile,
        content,
        size: new Blob([content]).size,
      });
      setSelectedFile(response.data);
      setFiles((currentFiles) =>
        currentFiles.map((file) => (file.id === response.data.id ? { ...file, ...response.data } : file))
      );
      setIsDirty(false);
    } catch (error) {
      console.error('Failed to save file:', error);
      setFileError('Failed to save file.');
    } finally {
      setIsSavingFile(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !conversations[0]) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setChatError(null);

    try {
      const response = await apiClient.sendMessage(projectId, conversations[0].id, inputMessage);
      setMessages((prev) => {
        const withoutOptimistic = prev.slice(0, -1);
        const nextMessages = [...withoutOptimistic, response.data.user_message];
        if (response.data.assistant_message) {
          nextMessages.push(response.data.assistant_message);
        }
        return nextMessages;
      });
      if (response.data.assistant_error) {
        setChatError(response.data.assistant_error);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setChatError('Failed to send message.');
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const getLanguageFromFile = (filename: string) => {
    const ext = filename.split('.').pop() || '';
    const languageMap: Record<string, string> = {
      py: 'python',
      js: 'javascript',
      ts: 'typescript',
      tsx: 'typescript',
      jsx: 'javascript',
      json: 'json',
      md: 'markdown',
      html: 'html',
      css: 'css',
    };
    return languageMap[ext] || 'plaintext';
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 px-4 py-3 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-foreground">{currentProject?.name || 'Project'}</h1>
        <div className="text-sm text-muted-foreground">{currentProject?.language}</div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden">
        {/* File Explorer */}
        <div className="w-64 border-r border-border bg-card/50 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="font-semibold text-foreground text-sm">Files</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            {files.length === 0 ? (
              <p className="text-sm text-muted-foreground p-2">No files</p>
            ) : (
              files.map((file) => (
                <button
                  key={file.id}
                  onClick={() => selectFile(file)}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                    selectedFile?.id === file.id
                      ? 'bg-primary/20 text-primary'
                      : 'text-foreground hover:bg-muted'
                  }`}
                >
                  {file.name}
                </button>
              ))
            )}
          </div>
        </div>

        {/* Editor Section */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {selectedFile ? (
            <>
              <div className="px-4 py-2 border-b border-border bg-card/50 text-sm text-muted-foreground flex items-center justify-between">
                <span>{selectedFile.path}</span>
                <div className="flex items-center gap-3">
                  {isDirty && <span className="text-xs text-primary">Unsaved changes</span>}
                  <span className="text-xs bg-muted px-2 py-1 rounded">{selectedFile.language || getLanguageFromFile(selectedFile.name)}</span>
                  <button
                    onClick={handleSaveFile}
                    disabled={!isDirty || isSavingFile}
                    className="px-3 py-1 bg-primary hover:bg-primary/90 disabled:opacity-50 text-primary-foreground rounded text-xs transition"
                  >
                    {isSavingFile ? 'Saving...' : 'Save'}
                  </button>
                </div>
              </div>
              {fileError && (
                <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm border-b border-destructive/20">
                  {fileError}
                </div>
              )}
              <div className="flex-1 overflow-hidden">
                <Editor
                  height="100%"
                  language={selectedFile.language || getLanguageFromFile(selectedFile.name)}
                  value={selectedFile.content || ''}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    wordWrap: 'on',
                    automaticLayout: true,
                  }}
                  onChange={(value) => {
                    if (selectedFile) {
                      setSelectedFile({ ...selectedFile, content: value || '' });
                      setIsDirty(true);
                    }
                  }}
                />
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              Select a file to view its content
            </div>
          )}
        </div>

        {/* Chat Sidebar */}
        <div className="w-80 border-l border-border bg-card/50 flex flex-col overflow-hidden">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="font-semibold text-foreground text-sm">AI Assistant</h2>
          </div>
          {chatError && (
            <div className="px-4 py-3 bg-destructive/10 text-destructive text-xs border-b border-destructive/20">
              {chatError}
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center mt-8">
                Start a conversation with the AI assistant to help with your code
              </p>
            ) : (
              messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted text-foreground'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-muted text-foreground px-3 py-2 rounded-lg">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-foreground rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-foreground rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-foreground rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-border p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask for help..."
                disabled={isLoading}
                className="flex-1 px-3 py-2 bg-background border border-border rounded text-sm text-foreground placeholder-muted-foreground focus:ring-2 focus:ring-primary disabled:opacity-50"
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className="px-3 py-2 bg-primary hover:bg-primary/90 disabled:opacity-50 text-primary-foreground rounded text-sm transition"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Terminal Toggle */}
      <div className="border-t border-border bg-card/50 px-4 py-2">
        <button
          onClick={() => setShowTerminal(!showTerminal)}
          className="text-sm text-muted-foreground hover:text-foreground transition"
        >
          {showTerminal ? '▼' : '▶'} Terminal
        </button>
        {showTerminal && (
          <div className="mt-2 p-2 bg-background rounded font-mono text-xs text-foreground border border-border">
            Ready to execute commands...
          </div>
        )}
      </div>
    </div>
  );
}

export default function WorkspacePage() {
  return (
    <ProtectedRoute>
      <WorkspaceContent />
    </ProtectedRoute>
  );
}
