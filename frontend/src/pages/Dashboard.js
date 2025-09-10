import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { 
  FileText, 
  Brain, 
  Search, 
  Upload,
  TrendingUp,
  Clock,
  BarChart3
} from 'lucide-react';
import { fetchDocumentStats, fetchConceptStats } from '../services/api';

const Dashboard = () => {
  const { data: docStats, isLoading: docStatsLoading } = useQuery(
    'documentStats',
    fetchDocumentStats
  );

  const { data: conceptStats, isLoading: conceptStatsLoading } = useQuery(
    'conceptStats',
    fetchConceptStats
  );

  const quickActions = [
    {
      name: 'Upload Document',
      description: 'Add new PDF or Word documents',
      href: '/upload',
      icon: Upload,
      color: 'bg-blue-500'
    },
    {
      name: 'Search Knowledge',
      description: 'Find documents and concepts',
      href: '/search',
      icon: Search,
      color: 'bg-green-500'
    },
    {
      name: 'Explore Concepts',
      description: 'Browse concept relationships',
      href: '/concepts',
      icon: Brain,
      color: 'bg-purple-500'
    },
    {
      name: 'View Analytics',
      description: 'Knowledge repository insights',
      href: '/analytics',
      icon: BarChart3,
      color: 'bg-orange-500'
    }
  ];

  const StatCard = ({ title, value, icon: Icon, loading, color = 'text-blue-600' }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className={`h-8 w-8 ${color}`} />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="text-lg font-medium text-gray-900">
              {loading ? (
                <div className="loading-spinner" />
              ) : (
                value?.toLocaleString() || '0'
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome to Your Second Brain
        </h1>
        <p className="text-gray-600">
          Your personal knowledge repository for Human-Computer Interaction documents. 
          Upload, search, and discover connections between concepts across your research.
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.name}
              to={action.href}
              className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-3 rounded-lg ${action.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-900">{action.name}</h3>
                  <p className="text-xs text-gray-500">{action.description}</p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Documents"
          value={docStats?.total_documents}
          icon={FileText}
          loading={docStatsLoading}
          color="text-blue-600"
        />
        <StatCard
          title="Total Concepts"
          value={conceptStats?.total_concepts}
          icon={Brain}
          loading={conceptStatsLoading}
          color="text-purple-600"
        />
        <StatCard
          title="Total Words"
          value={docStats?.total_words}
          icon={TrendingUp}
          loading={docStatsLoading}
          color="text-green-600"
        />
        <StatCard
          title="Concept Relations"
          value={conceptStats?.total_relations}
          icon={Clock}
          loading={conceptStatsLoading}
          color="text-orange-600"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Documents</h3>
          </div>
          <div className="p-6">
            {docStatsLoading ? (
              <div className="flex justify-center">
                <div className="loading-spinner" />
              </div>
            ) : docStats?.file_types?.length > 0 ? (
              <div className="space-y-3">
                {docStats.file_types.map((fileType, index) => (
                  <div key={index} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">{fileType.type}</span>
                    <span className="text-sm font-medium text-gray-900">
                      {fileType.count} files
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center">No documents uploaded yet</p>
            )}
            <div className="mt-4">
              <Link
                to="/documents"
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                View all documents →
              </Link>
            </div>
          </div>
        </div>

        {/* Top Concepts */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Top Concepts</h3>
          </div>
          <div className="p-6">
            {conceptStatsLoading ? (
              <div className="flex justify-center">
                <div className="loading-spinner" />
              </div>
            ) : conceptStats?.top_concepts?.length > 0 ? (
              <div className="space-y-3">
                {conceptStats.top_concepts.slice(0, 5).map((concept, index) => (
                  <div key={concept.id} className="flex justify-between items-center">
                    <Link
                      to={`/concepts/${concept.id}`}
                      className="text-sm text-gray-900 hover:text-blue-600 truncate"
                    >
                      {concept.name}
                    </Link>
                    <span className="text-xs text-gray-500 ml-2">
                      {concept.frequency}x
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center">No concepts extracted yet</p>
            )}
            <div className="mt-4">
              <Link
                to="/concepts"
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                Explore all concepts →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      {(!docStats?.total_documents || docStats.total_documents === 0) && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">
            Get Started with Your Second Brain
          </h3>
          <p className="text-blue-700 mb-4">
            Start building your knowledge repository by uploading your first document.
          </p>
          <Link
            to="/upload"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <Upload className="mr-2 h-4 w-4" />
            Upload Your First Document
          </Link>
        </div>
      )}
    </div>
  );
};

export default Dashboard;