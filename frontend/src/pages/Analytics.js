
import React from 'react';
import { useQuery } from 'react-query';
import { fetchDocumentStats, fetchConceptStats } from '../services/api';

export default function Analytics() {
  const { data: docStats, isLoading: docLoading } = useQuery('documentStats', fetchDocumentStats);
  const { data: conceptStats, isLoading: conceptLoading } = useQuery('conceptStats', fetchConceptStats);

  if (docLoading || conceptLoading) {
    return <div>Loading analytics...</div>;
  }

  if (!docStats || !conceptStats) {
    return <div>Unable to load analytics data.</div>;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Analytics</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Document Stats */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-2">Document Statistics</h2>
          <ul className="text-gray-700 space-y-1">
            <li>Total Documents: <span className="font-bold">{docStats.total_documents}</span></li>
            <li>Completed: <span className="font-bold">{docStats.completed_documents}</span></li>
            <li>Processing: <span className="font-bold">{docStats.processing_documents}</span></li>
            <li>Failed: <span className="font-bold">{docStats.failed_documents}</span></li>
            <li>Total Words: <span className="font-bold">{docStats.total_words}</span></li>
          </ul>
          <div className="mt-4">
            <h3 className="font-medium mb-1">File Types</h3>
            <ul className="text-sm text-gray-600">
              {docStats.file_types.map(ft => (
                <li key={ft.type}>{ft.type}: {ft.count}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* Concept Stats */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-2">Concept Statistics</h2>
          <ul className="text-gray-700 space-y-1">
            <li>Total Concepts: <span className="font-bold">{conceptStats.total_concepts}</span></li>
            <li>Total Relations: <span className="font-bold">{conceptStats.total_relations}</span></li>
          </ul>
          <div className="mt-4">
            <h3 className="font-medium mb-1">Top Categories</h3>
            <ul className="text-sm text-gray-600">
              {conceptStats.top_categories.map(cat => (
                <li key={cat.category}>{cat.category}: {cat.count}</li>
              ))}
            </ul>
          </div>
          <div className="mt-4">
            <h3 className="font-medium mb-1">Relation Types</h3>
            <ul className="text-sm text-gray-600">
              {conceptStats.relation_types.map(rt => (
                <li key={rt.type}>{rt.type}: {rt.count}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
