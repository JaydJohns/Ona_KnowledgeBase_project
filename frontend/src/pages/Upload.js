import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  Upload as UploadIcon, 
  FileText, 
  X, 
  CheckCircle,
  AlertCircle,
  Clock
} from 'lucide-react';
import { uploadDocument } from '../services/api';

const Upload = () => {
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState({});
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const uploadMutation = useMutation(
    ({ file, onProgress }) => uploadDocument(file, onProgress),
    {
      onSuccess: (data, variables) => {
        const fileId = variables.file.name;
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { ...prev[fileId], status: 'completed', document: data.document }
        }));
        
        // Invalidate queries to refresh data
        queryClient.invalidateQueries('documents');
        queryClient.invalidateQueries('documentStats');
        
        toast.success(`${variables.file.name} uploaded successfully!`);
      },
      onError: (error, variables) => {
        const fileId = variables.file.name;
        const errorMessage = error.response?.data?.error || 'Upload failed';
        
        setUploadProgress(prev => ({
          ...prev,
          [fileId]: { ...prev[fileId], status: 'error', error: errorMessage }
        }));
        
        toast.error(`Failed to upload ${variables.file.name}: ${errorMessage}`);
      }
    }
  );

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      errors.forEach(error => {
        if (error.code === 'file-too-large') {
          toast.error(`${file.name} is too large. Maximum size is 50MB.`);
        } else if (error.code === 'file-invalid-type') {
          toast.error(`${file.name} is not a supported file type. Please upload PDF or Word documents.`);
        } else {
          toast.error(`Error with ${file.name}: ${error.message}`);
        }
      });
    });

    // Add accepted files to the list
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: file.name + file.size + file.lastModified,
      name: file.name,
      size: file.size,
      type: file.type
    }));

    setFiles(prev => [...prev, ...newFiles]);

    // Initialize progress tracking
    const newProgress = {};
    newFiles.forEach(({ id }) => {
      newProgress[id] = { progress: 0, status: 'pending' };
    });
    setUploadProgress(prev => ({ ...prev, ...newProgress }));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxSize: 50 * 1024 * 1024, // 50MB
    multiple: true
  });

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileId];
      return newProgress;
    });
  };

  const uploadFile = async (fileItem) => {
    const fileId = fileItem.id;
    
    setUploadProgress(prev => ({
      ...prev,
      [fileId]: { ...prev[fileId], status: 'uploading', progress: 0 }
    }));

    const onProgress = (progress) => {
      setUploadProgress(prev => ({
        ...prev,
        [fileId]: { ...prev[fileId], progress }
      }));
    };

    uploadMutation.mutate({ file: fileItem.file, onProgress });
  };

  const uploadAllFiles = () => {
    const pendingFiles = files.filter(f => 
      !uploadProgress[f.id] || uploadProgress[f.id].status === 'pending'
    );
    
    pendingFiles.forEach(file => {
      uploadFile(file);
    });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (type) => {
    if (type.includes('pdf')) return '📄';
    if (type.includes('word') || type.includes('document')) return '📝';
    return '📄';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'uploading':
        return <Clock className="h-5 w-5 text-blue-500" />;
      default:
        return <FileText className="h-5 w-5 text-gray-400" />;
    }
  };

  const pendingFiles = files.filter(f => 
    !uploadProgress[f.id] || uploadProgress[f.id].status === 'pending'
  );
  const uploadingFiles = files.filter(f => 
    uploadProgress[f.id]?.status === 'uploading'
  );
  const completedFiles = files.filter(f => 
    uploadProgress[f.id]?.status === 'completed'
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
        <p className="text-gray-600">
          Add PDF, Word, Text, PowerPoint, and Excel documents to your knowledge repository
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <UploadIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        {isDragActive ? (
          <p className="text-lg text-blue-600">Drop the files here...</p>
        ) : (
          <div>
            <p className="text-lg text-gray-600 mb-2">
              Drag & drop files here, or click to select files
            </p>
            <p className="text-sm text-gray-500">
              Supports PDF, Word, Text, PowerPoint, and Excel documents (max 50MB each)
            </p>
          </div>
        )}
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              Files ({files.length})
            </h3>
            {pendingFiles.length > 0 && (
              <button
                onClick={uploadAllFiles}
                disabled={uploadMutation.isLoading}
                className="btn btn-primary"
              >
                Upload All ({pendingFiles.length})
              </button>
            )}
          </div>

          <div className="divide-y divide-gray-200">
            {files.map((fileItem) => {
              const progress = uploadProgress[fileItem.id];
              const status = progress?.status || 'pending';
              
              return (
                <div key={fileItem.id} className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center flex-1">
                      <div className="text-2xl mr-3">
                        {getFileIcon(fileItem.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {fileItem.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {formatFileSize(fileItem.size)}
                        </p>
                        
                        {/* Progress Bar */}
                        {status === 'uploading' && (
                          <div className="mt-2">
                            <div className="bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${progress.progress}%` }}
                              />
                            </div>
                            <p className="text-xs text-gray-500 mt-1">
                              {progress.progress}% uploaded
                            </p>
                          </div>
                        )}
                        
                        {/* Error Message */}
                        {status === 'error' && (
                          <p className="text-sm text-red-600 mt-1">
                            {progress.error}
                          </p>
                        )}
                        
                        {/* Success Message */}
                        {status === 'completed' && (
                          <p className="text-sm text-green-600 mt-1">
                            Upload completed successfully
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {getStatusIcon(status)}
                      
                      {status === 'pending' && (
                        <button
                          onClick={() => uploadFile(fileItem)}
                          disabled={uploadMutation.isLoading}
                          className="btn btn-primary btn-sm"
                        >
                          Upload
                        </button>
                      )}
                      
                      {status === 'completed' && (
                        <button
                          onClick={() => navigate(`/documents/${progress.document.id}`)}
                          className="btn btn-secondary btn-sm"
                        >
                          View
                        </button>
                      )}
                      
                      {status !== 'uploading' && (
                        <button
                          onClick={() => removeFile(fileItem.id)}
                          className="text-gray-400 hover:text-red-500"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Upload Summary */}
      {files.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-gray-900">{pendingFiles.length}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">{uploadingFiles.length}</p>
              <p className="text-sm text-gray-600">Uploading</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">{completedFiles.length}</p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">Tips for better results:</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Upload documents with clear, readable text for better concept extraction</li>
          <li>• PDF files with embedded text work better than scanned images</li>
          <li>• Word documents (.docx) are processed more accurately than older .doc files</li>
          <li>• Larger documents may take longer to process and analyze</li>
        </ul>
      </div>
    </div>
  );
};

export default Upload;