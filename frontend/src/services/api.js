import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Document API
export const fetchDocuments = async (params = {}) => {
  const response = await api.get('/documents', { params });
  return response.data;
};

export const fetchDocument = async (id) => {
  const response = await api.get(`/documents/${id}`);
  return response.data;
};

export const fetchDocumentContent = async (id) => {
  const response = await api.get(`/documents/${id}/content`);
  return response.data;
};

export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percentCompleted);
      }
    },
  });
  return response.data;
};

export const deleteDocument = async (id) => {
  const response = await api.delete(`/documents/${id}`);
  return response.data;
};

export const fetchDocumentStats = async () => {
  const response = await api.get('/documents/stats');
  return response.data;
};

// Concept API
export const fetchConcepts = async (params = {}) => {
  const response = await api.get('/concepts', { params });
  return response.data;
};

export const fetchConcept = async (id) => {
  const response = await api.get(`/concepts/${id}`);
  return response.data;
};

export const fetchConceptCategories = async () => {
  const response = await api.get('/concepts/categories');
  return response.data;
};

export const fetchConceptGraph = async (params = {}) => {
  const response = await api.get('/concepts/graph', { params });
  return response.data;
};

export const analyzeDocumentConcepts = async (documentId) => {
  const response = await api.post(`/concepts/analyze/${documentId}`);
  return response.data;
};

export const fetchConceptRelations = async (params = {}) => {
  const response = await api.get('/concepts/relations', { params });
  return response.data;
};

export const fetchSimilarDocuments = async (documentId, limit = 5) => {
  const response = await api.get(`/concepts/similar/${documentId}`, {
    params: { limit }
  });
  return response.data;
};

export const fetchConceptStats = async () => {
  const response = await api.get('/concepts/stats');
  return response.data;
};

export const mergeConcepts = async (primaryId, secondaryId) => {
  const response = await api.post('/concepts/merge', {
    primary_id: primaryId,
    secondary_id: secondaryId
  });
  return response.data;
};

// Search API
export const searchDocuments = async (params = {}) => {
  const response = await api.get('/search', { params });
  return response.data;
};

export const getSearchSuggestions = async (query, limit = 10) => {
  const response = await api.get('/search/suggestions', {
    params: { q: query, limit }
  });
  return response.data;
};

export const getSearchAnalytics = async () => {
  const response = await api.get('/search/analytics');
  return response.data;
};

export const reindexDocuments = async () => {
  const response = await api.post('/search/reindex');
  return response.data;
};

export const findSimilarDocuments = async (documentId, limit = 5) => {
  const response = await api.get('/search/similar', {
    params: { document_id: documentId, limit }
  });
  return response.data;
};

export const advancedSearch = async (searchData) => {
  const response = await api.post('/search/advanced', searchData);
  return response.data;
};

// Utility functions
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatDate = (dateString) => {
  if (!dateString) return 'Unknown';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const getFileTypeIcon = (fileType) => {
  if (fileType?.includes('pdf')) return '📄';
  if (fileType?.includes('word') || fileType?.includes('document')) return '📝';
  return '📄';
};

export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export default api;