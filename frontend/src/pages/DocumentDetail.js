
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { fetchDocument, fetchDocumentContent, fetchSimilarDocuments, formatFileSize, formatDate } from '../services/api';

export default function DocumentDetail() {
  const { id } = useParams();
  const docId = Number(id);

  const { data: docData, isLoading: docLoading } = useQuery(['document', docId], () => fetchDocument(docId));
  const { data: contentData, isLoading: contentLoading } = useQuery(['documentContent', docId], () => fetchDocumentContent(docId));
  const { data: similarDocs, isLoading: similarLoading } = useQuery(['similarDocuments', docId], () => fetchSimilarDocuments(docId, 5));

  if (docLoading || contentLoading) return <div>Loading document...</div>;
  if (!docData || !docData.document) return <div>Document not found.</div>;

  const doc = docData.document;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">{doc.title || doc.original_filename}</h1>
      <div className="text-sm text-gray-500 mb-2">
        {doc.file_type} • {formatFileSize(doc.file_size)} • {doc.word_count} words
      </div>
      <div className="text-xs text-gray-400 mb-4">
        Uploaded: {formatDate(doc.upload_date)} | Processed: {formatDate(doc.processed_date)}
      </div>
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-1">Summary</h2>
        <div className="bg-gray-50 rounded p-3 text-gray-800">
          {contentData?.summary || doc.summary || 'No summary available.'}
        </div>
      </div>
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-1">Content</h2>
        <div className="bg-white rounded p-3 text-gray-900 whitespace-pre-line max-h-96 overflow-auto">
          {contentData?.content || 'No content available.'}
        </div>
      </div>
      {/* Related Documents */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold mb-1">Similar Documents</h2>
        {similarLoading ? (
          <div>Loading similar documents...</div>
        ) : similarDocs && similarDocs.similar_documents && similarDocs.similar_documents.length > 0 ? (
          <ul className="list-disc pl-5 space-y-1">
            {similarDocs.similar_documents.map(sim => (
              <li key={sim.id}>
                <Link to={`/documents/${sim.id}`} className="text-blue-700 hover:underline">
                  {sim.title || sim.original_filename}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <div className="text-gray-500">No similar documents found.</div>
        )}
      </div>
    </div>
  );
}
