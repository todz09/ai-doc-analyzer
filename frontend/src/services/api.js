import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const askQuestion = async (docId, question, chatHistory = []) => {
  const response = await api.post('/api/chat', {
    doc_id: docId,
    question,
    chat_history: chatHistory,
  });

  return response.data;
};

export const listDocuments = async () => {
  const response = await api.get('/api/upload/documents');
  return response.data;
};

export const deleteDocument = async (docId) => {
  const response = await api.delete(`/api/upload/${docId}`);
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
