import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const History = () => {
  const [datasets, setDatasets] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [historyStatus, setHistoryStatus] = useState(null);

  useEffect(() => {
    fetchHistory(currentPage);
    fetchHistoryStatus();
  }, [currentPage]);

  const fetchHistory = async (page = 1) => {
    try {
      setLoading(true);
      const response = await api.get(`/api/history/datasets/?page=${page}&page_size=10`);
      setDatasets(response.data.datasets || []);
      setPagination(response.data.pagination);
    } catch (err) {
      console.error('Error fetching history:', err);
      setError('Failed to load dataset history');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoryStatus = async () => {
    try {
      const response = await api.get('/api/history/status/');
      setHistoryStatus(response.data);
    } catch (err) {
      console.warn('Could not fetch history status:', err);
    }
  };

  const handleDelete = async (datasetId, datasetName) => {
    if (!window.confirm(`Are you sure you want to delete "${datasetName}"?`)) {
      return;
    }

    try {
      await api.delete(`/api/history/datasets/${datasetId}/`, {
        data: { confirm: true }
      });
      
      // Refresh the current page
      fetchHistory(currentPage);
      fetchHistoryStatus();
    } catch (err) {
      console.error('Error deleting dataset:', err);
      alert('Failed to delete dataset');
    }
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  if (loading && datasets.length === 0) {
    return <div className="loading">Loading history...</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Dataset History</h1>
        <Link to="/upload" className="btn btn-primary">
          Upload New Dataset
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {/* History Status */}
      {historyStatus && (
        <div className="card">
          <h2>Storage Overview</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{historyStatus.history_info?.total_datasets || 0}</h3>
              <p>Total Datasets</p>
            </div>
            <div className="stat-card">
              <h3>{historyStatus.history_info?.processed_datasets || 0}</h3>
              <p>Processed Datasets</p>
            </div>
            <div className="stat-card">
              <h3>{historyStatus.settings?.max_datasets_allowed || 5}</h3>
              <p>Max Allowed</p>
            </div>
            <div className="stat-card">
              <h3>{historyStatus.cleanup_preview?.datasets_to_be_deleted || 0}</h3>
              <p>Pending Cleanup</p>
            </div>
          </div>
          
          {historyStatus.cleanup_preview?.datasets_to_be_deleted > 0 && (
            <div className="alert alert-info" style={{ marginTop: '15px' }}>
              <strong>Note:</strong> {historyStatus.cleanup_preview.datasets_to_be_deleted} datasets 
              are scheduled for automatic cleanup when the limit is exceeded.
            </div>
          )}
        </div>
      )}

      {/* Dataset History Table */}
      <div className="card">
        <h2>All Datasets ({pagination?.total_count || 0})</h2>
        
        {datasets.length === 0 ? (
          <p>No datasets found. <Link to="/upload">Upload your first dataset</Link></p>
        ) : (
          <>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>File Name</th>
                    <th>Size</th>
                    <th>Rows</th>
                    <th>Columns</th>
                    <th>Upload Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map((dataset) => (
                    <tr key={dataset.id}>
                      <td>
                        <strong>{dataset.name}</strong>
                        {dataset.description && (
                          <div style={{ fontSize: '12px', color: '#666', marginTop: '2px' }}>
                            {dataset.description.length > 40 
                              ? `${dataset.description.substring(0, 40)}...` 
                              : dataset.description
                            }
                          </div>
                        )}
                      </td>
                      <td>{dataset.file_name}</td>
                      <td>{formatFileSize(dataset.file_size)}</td>
                      <td>{dataset.total_rows?.toLocaleString() || 'N/A'}</td>
                      <td>{dataset.total_columns || 'N/A'}</td>
                      <td>
                        <div>{new Date(dataset.upload_date).toLocaleDateString()}</div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          {new Date(dataset.upload_date).toLocaleTimeString()}
                        </div>
                      </td>
                      <td>
                        <span style={{ 
                          color: dataset.is_processed ? 'green' : 'orange',
                          fontWeight: 'bold'
                        }}>
                          {dataset.is_processed ? 'Processed' : 'Processing'}
                        </span>
                        {dataset.summary && (
                          <div style={{ fontSize: '11px', color: '#666', marginTop: '2px' }}>
                            {dataset.summary.equipment_types > 0 && 
                              `${dataset.summary.equipment_types} equipment types`
                            }
                          </div>
                        )}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                          <Link 
                            to={`/datasets/${dataset.id}`} 
                            className="btn btn-primary"
                            style={{ fontSize: '12px', padding: '4px 8px' }}
                          >
                            View
                          </Link>
                          <button
                            onClick={() => handleDelete(dataset.id, dataset.name)}
                            className="btn btn-danger"
                            style={{ fontSize: '12px', padding: '4px 8px' }}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination && pagination.total_pages > 1 && (
              <div className="pagination">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={!pagination.has_previous}
                  className="btn btn-secondary"
                >
                  Previous
                </button>
                
                <span style={{ margin: '0 15px' }}>
                  Page {pagination.page} of {pagination.total_pages}
                </span>
                
                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={!pagination.has_next}
                  className="btn btn-secondary"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Quick Stats */}
      {datasets.length > 0 && (
        <div className="card">
          <h3>Quick Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{datasets.reduce((sum, d) => sum + (d.total_rows || 0), 0).toLocaleString()}</h3>
              <p>Total Rows (Current Page)</p>
            </div>
            <div className="stat-card">
              <h3>{datasets.filter(d => d.is_processed).length}</h3>
              <p>Processed (Current Page)</p>
            </div>
            <div className="stat-card">
              <h3>{datasets.reduce((sum, d) => sum + (d.file_size || 0), 0) / 1024 / 1024 / 1024 < 1 
                ? `${(datasets.reduce((sum, d) => sum + (d.file_size || 0), 0) / 1024 / 1024).toFixed(1)} MB`
                : `${(datasets.reduce((sum, d) => sum + (d.file_size || 0), 0) / 1024 / 1024 / 1024).toFixed(2)} GB`
              }</h3>
              <p>Total Size (Current Page)</p>
            </div>
            <div className="stat-card">
              <h3>{Math.round(datasets.reduce((sum, d) => sum + (d.total_columns || 0), 0) / datasets.length) || 0}</h3>
              <p>Avg Columns (Current Page)</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;