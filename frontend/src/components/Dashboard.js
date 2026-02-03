import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [recentDatasets, setRecentDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch datasets list
      const datasetsResponse = await api.get('/api/datasets/');
      const datasets = datasetsResponse.data.results || [];
      
      // Get recent datasets (last 5)
      const recent = datasets.slice(0, 5);
      setRecentDatasets(recent);
      
      // Calculate basic stats
      const totalDatasets = datasets.length;
      const processedDatasets = datasets.filter(d => d.is_processed).length;
      const totalRows = datasets.reduce((sum, d) => sum + (d.total_rows || 0), 0);
      const totalColumns = datasets.reduce((sum, d) => sum + (d.total_columns || 0), 0);
      
      setStats({
        totalDatasets,
        processedDatasets,
        totalRows,
        averageColumns: totalDatasets > 0 ? Math.round(totalColumns / totalDatasets) : 0
      });
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Stats Overview */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <h3>{stats.totalDatasets}</h3>
            <p>Total Datasets</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <h3>{stats.processedDatasets}</h3>
            <p>Processed Datasets</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <h3>{stats.totalRows.toLocaleString()}</h3>
            <p>Total Rows</p>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <h3>{stats.averageColumns}</h3>
            <p>Avg Columns</p>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="card">
        <h2>Quick Actions</h2>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <Link to="/upload" className="btn btn-primary">
            Upload New Dataset
          </Link>
          <Link to="/datasets" className="btn btn-secondary">
            View All Datasets
          </Link>
          <Link to="/history" className="btn btn-secondary">
            View History
          </Link>
        </div>
      </div>

      {/* Recent Datasets */}
      <div className="card">
        <h2>Recent Datasets</h2>
        {recentDatasets.length === 0 ? (
          <p>No datasets uploaded yet. <Link to="/upload">Upload your first dataset</Link></p>
        ) : (
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>File Name</th>
                  <th>Rows</th>
                  <th>Columns</th>
                  <th>Upload Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentDatasets.map((dataset) => (
                  <tr key={dataset.id}>
                    <td>{dataset.name}</td>
                    <td>{dataset.file_name}</td>
                    <td>{dataset.total_rows?.toLocaleString() || 'N/A'}</td>
                    <td>{dataset.total_columns || 'N/A'}</td>
                    <td>{new Date(dataset.upload_date).toLocaleDateString()}</td>
                    <td>
                      <span style={{ 
                        color: dataset.is_processed ? 'green' : 'orange',
                        fontWeight: 'bold'
                      }}>
                        {dataset.is_processed ? 'Processed' : 'Processing'}
                      </span>
                    </td>
                    <td>
                      <Link 
                        to={`/datasets/${dataset.id}`} 
                        className="btn btn-primary"
                        style={{ fontSize: '12px', padding: '5px 10px' }}
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;