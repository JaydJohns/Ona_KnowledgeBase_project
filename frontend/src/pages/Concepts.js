import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Grid, 
  List,
  Brain,
  TrendingUp,
  Eye,
  Network
} from 'lucide-react';
import ConceptGraph from '../components/ConceptGraph';
import { 
  fetchConcepts, 
  fetchConceptCategories, 
  fetchConceptGraph 
} from '../services/api';

const Concepts = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('frequency');
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'graph'
  const [page, setPage] = useState(1);
  const [graphMinStrength, setGraphMinStrength] = useState(0.3);

  const { data: conceptsData, isLoading: conceptsLoading } = useQuery(
    ['concepts', { 
      page, 
      search: searchTerm, 
      category: selectedCategory, 
      sort_by: sortBy 
    }],
    () => fetchConcepts({ 
      page, 
      search: searchTerm, 
      category: selectedCategory, 
      sort_by: sortBy,
      per_page: 20
    }),
    { keepPreviousData: true }
  );

  const { data: categoriesData } = useQuery(
    'conceptCategories',
    fetchConceptCategories
  );

  const { data: graphData, isLoading: graphLoading } = useQuery(
    ['conceptGraph', { category: selectedCategory, min_strength: graphMinStrength }],
    () => fetchConceptGraph({ 
      category: selectedCategory, 
      min_strength: graphMinStrength 
    }),
    { enabled: viewMode === 'graph' }
  );

  const handleConceptClick = (concept) => {
    // Navigate to concept detail or show more info
    console.log('Concept clicked:', concept);
  };

  const ConceptCard = ({ concept }) => (
    <Link
      to={`/concepts/${concept.id}`}
      className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow p-4"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-medium text-gray-900 mb-1">{concept.name}</h3>
          {concept.description && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
              {concept.description}
            </p>
          )}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center">
              <TrendingUp className="h-3 w-3 mr-1" />
              {concept.frequency} occurrences
            </span>
            {concept.category && (
              <span className="px-2 py-1 bg-gray-100 rounded-full">
                {concept.category.replace(/_/g, ' ')}
              </span>
            )}
          </div>
        </div>
        <div className="ml-4">
          <Eye className="h-4 w-4 text-gray-400" />
        </div>
      </div>
    </Link>
  );

  const ListView = () => (
    <div className="space-y-4">
      {conceptsLoading ? (
        <div className="flex justify-center py-8">
          <div className="loading-spinner" />
        </div>
      ) : conceptsData?.concepts?.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {conceptsData.concepts.map((concept) => (
              <ConceptCard key={concept.id} concept={concept} />
            ))}
          </div>
          
          {/* Pagination */}
          {conceptsData.pages > 1 && (
            <div className="flex justify-center items-center gap-2 mt-6">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {conceptsData.pages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(conceptsData.pages, p + 1))}
                disabled={page === conceptsData.pages}
                className="px-3 py-1 text-sm border rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No concepts found</p>
          <p className="text-sm text-gray-400">
            Try adjusting your search or upload more documents
          </p>
        </div>
      )}
    </div>
  );

  const GraphView = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Concept Network</h3>
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Min Strength:</label>
            <input
              type="range"
              min="0.1"
              max="1"
              step="0.1"
              value={graphMinStrength}
              onChange={(e) => setGraphMinStrength(parseFloat(e.target.value))}
              className="w-20"
            />
            <span className="text-sm text-gray-600">{graphMinStrength}</span>
          </div>
        </div>
      </div>
      
      <div className="p-4">
        {graphLoading ? (
          <div className="flex justify-center items-center h-96">
            <div className="loading-spinner" />
          </div>
        ) : (
          <ConceptGraph
            data={graphData}
            onNodeClick={handleConceptClick}
            width={800}
            height={600}
            showControls={true}
          />
        )}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Concepts</h1>
          <p className="text-gray-600">
            Explore concepts and their relationships across your documents
          </p>
        </div>
        
        {/* View Mode Toggle */}
        <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('list')}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'list'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <List className="h-4 w-4" />
            List
          </button>
          <button
            onClick={() => setViewMode('graph')}
            className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'graph'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Network className="h-4 w-4" />
            Graph
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search concepts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input"
            >
              <option value="">All Categories</option>
              {categoriesData?.categories?.map((category) => (
                <option key={category.name} value={category.name}>
                  {category.name.replace(/_/g, ' ')} ({category.count})
                </option>
              ))}
            </select>
          </div>

          {/* Sort */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="input"
            >
              <option value="frequency">Sort by Frequency</option>
              <option value="name">Sort by Name</option>
              <option value="created_date">Sort by Date</option>
            </select>
          </div>

          {/* Stats */}
          <div className="flex items-center text-sm text-gray-600">
            <Filter className="h-4 w-4 mr-2" />
            {conceptsData?.total || 0} concepts
          </div>
        </div>
      </div>

      {/* Content */}
      {viewMode === 'list' ? <ListView /> : <GraphView />}
    </div>
  );
};

export default Concepts;