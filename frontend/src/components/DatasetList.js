import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const DatasetList = () => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/datasets/');
      setDatasets(response.data.results || []);
    } catch (err) {
      console.error('Error fetching datasets:', err);
      setError('Failed to load datasets');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (datasetId, datasetName) => {
    if (!window.confirm(`Are you sure you want to delete "${datasetName}"?`)) {
      return;
    }

    try {
      await api.delete(`/api/datasets/${datasetId}/delete_dataset/`);
      setDatasets(datasets.filter(d => d.id !== datasetId));
    } catch (err) {
      console.error('Error deleting dataset:', err);
      alert('Failed to delete dataset');
    }
  };

  const handleDownloadPDF = async (datasetId, datasetName) => {
    try {
      const response = await api.get(`/api/reports/pdf/${datasetId}/`, {
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${datasetName}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      alert('Failed to generate PDF report');
    }
  };

  if (loading) {
    return <div className="loading">Loading datasets...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Datasets</h1>
        <Link to="/upload" className="btn btn-primary">
          Upload New Dataset
        </Link>
      </div>

      {datasets.length === 0 ? (
        <div className="card">
          <p>No datasets found. <Link to="/upload">Upload your first dataset</Link></p>
        </div>
      ) : (
        <div className="card">
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>File Name</th>
                  <th>Type</th>
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
                          {dataset.description.length > 50 
                            ? `${dataset.description.substring(0, 50)}...` 
                            : dataset.description
                          }
                        </div>
                      )}
                    </td>
                    <td>{dataset.file_name}</td>
                    <td>{dataset.file_type?.toUpperCase() || 'CSV'}</td>
                    <td>
                      {dataset.file_size 
                        ? `${(dataset.file_size / 1024 / 1024).toFixed(2)} MB`
                        : 'N/A'
                      }
                    </td>
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
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <Link 
                          to={`/datasets/${dataset.id}`} 
                          className="btn btn-primary"
                          style={{ fontSize: '12px', padding: '5px 10px' }}
                        >
                          View
                        </Link>
                        {dataset.is_processed && (
                          <button
                            onClick={() => handleDownloadPDF(dataset.id, dataset.name)}
                            className="btn btn-success"
                            style={{ fontSize: '12px', padding: '5px 10px' }}
                            title="Download PDF Report"
                          >
                            📄 PDF
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(dataset.id, dataset.name)}
                          className="btn btn-danger"
                          style={{ fontSize: '12px', padding: '5px 10px' }}
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
        </div>
      )}
    </div>
  );
};

export default DatasetList;