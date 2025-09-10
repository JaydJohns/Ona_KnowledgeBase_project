
import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { fetchDocuments, formatFileSize, formatDate } from '../services/api';
import { Link } from 'react-router-dom';

export default function Documents() {
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  const { data, isLoading, isError } = useQuery(
    ['documents', page, perPage],
    () => fetchDocuments({ page, per_page: perPage }),
    { keepPreviousData: true }
  );

  if (isLoading) return <div>Loading documents...</div>;
  if (isError || !data) return <div>Failed to load documents.</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Documents</h1>
      <div className="flex items-center gap-4 mb-4">
        <label>
          Per page:
          <select
            className="input ml-2"
            value={perPage}
            onChange={e => { setPerPage(Number(e.target.value)); setPage(1); }}
          >
            {[10, 20, 50].map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
      </div>
      <div className="bg-white rounded-lg shadow divide-y">
        {data.documents.length === 0 ? (
          <div className="p-4 text-gray-500">No documents found.</div>
        ) : (
          data.documents.map(doc => (
            <div key={doc.id} className="p-4 flex items-center justify-between">
              <div>
                <Link to={`/documents/${doc.id}`} className="text-lg font-semibold text-blue-700 hover:underline">
                  {doc.title || doc.original_filename}
                </Link>
                <div className="text-sm text-gray-500">{doc.file_type} • {formatFileSize(doc.file_size)} • {doc.word_count} words</div>
                <div className="text-xs text-gray-400">Uploaded: {formatDate(doc.upload_date)}</div>
                <div className="text-xs text-gray-400">Status: {doc.processing_status}</div>
              </div>
              <div>
                <Link to={`/documents/${doc.id}`} className="btn btn-secondary btn-sm">View</Link>
              </div>
            </div>
          ))
        )}
      </div>
      {/* Pagination */}
      <div className="flex items-center gap-2 mt-4">
        <button
          className="btn btn-secondary"
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </button>
        <span>Page {page} of {data.pages}</span>
        <button
          className="btn btn-secondary"
          onClick={() => setPage(p => Math.min(data.pages, p + 1))}
          disabled={page === data.pages}
        >
          Next
        </button>
      </div>
    </div>
  );
}
