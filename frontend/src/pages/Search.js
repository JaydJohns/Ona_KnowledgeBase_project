
import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { searchDocuments, getSearchSuggestions } from '../services/api';
import { Link } from 'react-router-dom';

export default function Search() {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('hybrid');
  const [limit, setLimit] = useState(20);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedSuggestion, setSelectedSuggestion] = useState(null);

  const { data: suggestions } = useQuery(
    ['searchSuggestions', query],
    () => getSearchSuggestions(query),
    { enabled: query.length > 1 }
  );

  const { data: searchResults, isLoading } = useQuery(
    ['searchResults', query, searchType, limit],
    () => searchDocuments({ q: query, type: searchType, limit }),
    { enabled: !!query }
  );

  const handleInputChange = (e) => {
    setQuery(e.target.value);
    setShowSuggestions(true);
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    setSelectedSuggestion(suggestion);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Search</h1>
      <div className="flex flex-col md:flex-row gap-4 items-center">
        <input
          className="input w-full md:w-1/2"
          type="text"
          placeholder="Search documents, concepts, or keywords..."
          value={query}
          onChange={handleInputChange}
          onFocus={() => setShowSuggestions(true)}
        />
        <select
          className="input"
          value={searchType}
          onChange={e => setSearchType(e.target.value)}
        >
          <option value="hybrid">Hybrid</option>
          <option value="keyword">Keyword</option>
          <option value="semantic">Semantic</option>
          <option value="concept">Concept</option>
        </select>
        <input
          className="input w-24"
          type="number"
          min={1}
          max={100}
          value={limit}
          onChange={e => setLimit(Number(e.target.value))}
        />
      </div>

      {/* Suggestions */}
      {showSuggestions && suggestions && suggestions.suggestions && suggestions.suggestions.length > 0 && (
        <div className="bg-white border rounded shadow p-2 max-w-md">
          <ul>
            {suggestions.suggestions.map((s, i) => (
              <li
                key={i}
                className="cursor-pointer hover:bg-blue-100 px-2 py-1"
                onClick={() => handleSuggestionClick(s)}
              >
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Results */}
      <div>
        {isLoading && <div>Searching...</div>}
        {searchResults && searchResults.results && searchResults.results.length > 0 ? (
          <div className="space-y-4 mt-4">
            {searchResults.results.map((result, idx) => (
              <div key={idx} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <Link to={`/documents/${result.document.id}`} className="text-lg font-semibold text-blue-700 hover:underline">
                      {result.document.title}
                    </Link>
                    <div className="text-sm text-gray-500">{result.document.file_type} • {result.document.word_count} words</div>
                    <div className="text-xs text-gray-400">Uploaded: {result.document.upload_date}</div>
                  </div>
                  <div className="text-right">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      Score: {result.score.toFixed(2)}
                    </span>
                  </div>
                </div>
                <div className="mt-2 text-gray-700">
                  {result.document.summary}
                </div>
                {result.highlights && result.highlights.length > 0 && (
                  <div className="mt-2 text-sm text-yellow-800">
                    <strong>Highlights:</strong> {result.highlights.join(' ... ')}
                  </div>
                )}
                {result.matched_concepts && result.matched_concepts.length > 0 && (
                  <div className="mt-2 text-sm text-green-700">
                    <strong>Matched Concepts:</strong> {result.matched_concepts.join(', ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          !isLoading && query && <div className="text-gray-500 mt-4">No results found.</div>
        )}
      </div>
    </div>
  );
}
