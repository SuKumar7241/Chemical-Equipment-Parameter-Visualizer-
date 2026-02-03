import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Bar, Line, Pie } from 'react-chartjs-2';
import api from '../services/api';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const DatasetDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [dataset, setDataset] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchDatasetDetails();
  }, [id]);

  const fetchDatasetDetails = async () => {
    try {
      setLoading(true);
      
      // Fetch dataset details
      const datasetResponse = await api.get(`/api/datasets/${id}/`);
      setDataset(datasetResponse.data);
      
      // Fetch statistics if dataset is processed
      if (datasetResponse.data.is_processed) {
        try {
          const statsResponse = await api.get(`/api/datasets/${id}/statistics/`);
          setStatistics(statsResponse.data);
        } catch (statsErr) {
          console.warn('Statistics not available:', statsErr);
        }
        
        try {
          const columnsResponse = await api.get(`/api/datasets/${id}/columns/`);
          setColumns(columnsResponse.data);
        } catch (colErr) {
          console.warn('Columns not available:', colErr);
        }
      }
      
    } catch (err) {
      console.error('Error fetching dataset details:', err);
      setError('Failed to load dataset details');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${dataset.name}"?`)) {
      return;
    }

    try {
      await api.delete(`/api/datasets/${id}/delete_dataset/`);
      navigate('/datasets');
    } catch (err) {
      console.error('Error deleting dataset:', err);
      alert('Failed to delete dataset');
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await api.get(`/api/reports/pdf/${id}/`, {
        responseType: 'blob'
      });
      
      // Create blob link to download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${dataset.name}_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error downloading PDF:', err);
      alert('Failed to generate PDF report');
    }
  };

  const generateChartData = () => {
    if (!statistics || !statistics.statistics_data) return null;

    const stats = statistics.statistics_data;
    const charts = {};

    // Generate numeric columns chart
    const numericColumns = Object.keys(stats).filter(col => 
      stats[col] && typeof stats[col].mean === 'number'
    );

    if (numericColumns.length > 0) {
      charts.numericMeans = {
        labels: numericColumns,
        datasets: [{
          label: 'Mean Values',
          data: numericColumns.map(col => stats[col].mean),
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      };
    }

    // Generate data type distribution
    const dataTypes = {};
    columns.forEach(col => {
      dataTypes[col.data_type] = (dataTypes[col.data_type] || 0) + 1;
    });

    if (Object.keys(dataTypes).length > 0) {
      charts.dataTypes = {
        labels: Object.keys(dataTypes),
        datasets: [{
          data: Object.values(dataTypes),
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 205, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)',
            'rgba(153, 102, 255, 0.6)',
          ]
        }]
      };
    }

    return charts;
  };

  if (loading) {
    return <div className="loading">Loading dataset details...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  if (!dataset) {
    return <div className="alert alert-error">Dataset not found</div>;
  }

  const charts = generateChartData();

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>{dataset.name}</h1>
        <div>
          <Link to="/datasets" className="btn btn-secondary" style={{ marginRight: '10px' }}>
            Back to Datasets
          </Link>
          {dataset.is_processed && (
            <button 
              onClick={handleDownloadPDF} 
              className="btn btn-primary" 
              style={{ marginRight: '10px' }}
            >
              📄 Download PDF Report
            </button>
          )}
          <button onClick={handleDelete} className="btn btn-danger">
            Delete Dataset
          </button>
        </div>
      </div>

      {/* Dataset Info Card */}
      <div className="card">
        <h2>Dataset Information</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          <div>
            <strong>File Name:</strong> {dataset.file_name}
          </div>
          <div>
            <strong>File Size:</strong> {dataset.file_size ? `${(dataset.file_size / 1024 / 1024).toFixed(2)} MB` : 'N/A'}
          </div>
          <div>
            <strong>Upload Date:</strong> {new Date(dataset.upload_date).toLocaleString()}
          </div>
          <div>
            <strong>Status:</strong> 
            <span style={{ 
              color: dataset.is_processed ? 'green' : 'orange',
              fontWeight: 'bold',
              marginLeft: '5px'
            }}>
              {dataset.is_processed ? 'Processed' : 'Processing'}
            </span>
          </div>
          <div>
            <strong>Rows:</strong> {dataset.total_rows?.toLocaleString() || 'N/A'}
          </div>
          <div>
            <strong>Columns:</strong> {dataset.total_columns || 'N/A'}
          </div>
        </div>
        {dataset.description && (
          <div style={{ marginTop: '15px' }}>
            <strong>Description:</strong> {dataset.description}
          </div>
        )}
      </div>

      {!dataset.is_processed ? (
        <div className="alert alert-info">
          Dataset is still being processed. Statistics and charts will be available once processing is complete.
        </div>
      ) : (
        <>
          {/* Tab Navigation */}
          <div className="card">
            <div style={{ borderBottom: '1px solid #ddd', marginBottom: '20px' }}>
              <div style={{ display: 'flex', gap: '20px' }}>
                <button
                  onClick={() => setActiveTab('overview')}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '10px 0',
                    borderBottom: activeTab === 'overview' ? '2px solid #007bff' : 'none',
                    color: activeTab === 'overview' ? '#007bff' : '#666',
                    cursor: 'pointer'
                  }}
                >
                  Overview
                </button>
                <button
                  onClick={() => setActiveTab('columns')}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '10px 0',
                    borderBottom: activeTab === 'columns' ? '2px solid #007bff' : 'none',
                    color: activeTab === 'columns' ? '#007bff' : '#666',
                    cursor: 'pointer'
                  }}
                >
                  Columns
                </button>
                <button
                  onClick={() => setActiveTab('charts')}
                  style={{
                    background: 'none',
                    border: 'none',
                    padding: '10px 0',
                    borderBottom: activeTab === 'charts' ? '2px solid #007bff' : 'none',
                    color: activeTab === 'charts' ? '#007bff' : '#666',
                    cursor: 'pointer'
                  }}
                >
                  Charts
                </button>
              </div>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && statistics && (
              <div>
                <h3>Statistics Summary</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <h3>{statistics.total_records || dataset.total_rows}</h3>
                    <p>Total Records</p>
                  </div>
                  <div className="stat-card">
                    <h3>{statistics.numeric_columns_count}</h3>
                    <p>Numeric Columns</p>
                  </div>
                  <div className="stat-card">
                    <h3>{statistics.categorical_columns_count}</h3>
                    <p>Categorical Columns</p>
                  </div>
                  <div className="stat-card">
                    <h3>{statistics.missing_values_count}</h3>
                    <p>Missing Values</p>
                  </div>
                </div>
                
                {/* Equipment-specific stats if available */}
                {(statistics.avg_flowrate || statistics.avg_pressure || statistics.avg_temperature) && (
                  <div>
                    <h3>Equipment Statistics</h3>
                    <div className="stats-grid">
                      {statistics.avg_flowrate && (
                        <div className="stat-card">
                          <h3>{statistics.avg_flowrate.toFixed(2)}</h3>
                          <p>Avg Flow Rate</p>
                        </div>
                      )}
                      {statistics.avg_pressure && (
                        <div className="stat-card">
                          <h3>{statistics.avg_pressure.toFixed(2)}</h3>
                          <p>Avg Pressure</p>
                        </div>
                      )}
                      {statistics.avg_temperature && (
                        <div className="stat-card">
                          <h3>{statistics.avg_temperature.toFixed(2)}</h3>
                          <p>Avg Temperature</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'columns' && (
              <div>
                <h3>Column Information</h3>
                {columns.length > 0 ? (
                  <div className="table-container">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Column Name</th>
                          <th>Data Type</th>
                          <th>Non-Null Count</th>
                          <th>Null Count</th>
                        </tr>
                      </thead>
                      <tbody>
                        {columns.map((column, index) => (
                          <tr key={index}>
                            <td><strong>{column.column_name}</strong></td>
                            <td>{column.data_type}</td>
                            <td>{column.non_null_count}</td>
                            <td>{column.null_count}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p>Column information not available</p>
                )}
              </div>
            )}

            {activeTab === 'charts' && (
              <div>
                <h3>Data Visualization</h3>
                {charts ? (
                  <div>
                    {charts.numericMeans && (
                      <div className="chart-container">
                        <h4>Numeric Column Means</h4>
                        <Bar 
                          data={charts.numericMeans}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: {
                                position: 'top',
                              },
                              title: {
                                display: true,
                                text: 'Mean Values by Column'
                              }
                            }
                          }}
                        />
                      </div>
                    )}
                    
                    {charts.dataTypes && (
                      <div className="chart-container">
                        <h4>Data Type Distribution</h4>
                        <Pie 
                          data={charts.dataTypes}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: {
                                position: 'right',
                              },
                              title: {
                                display: true,
                                text: 'Column Data Types'
                              }
                            }
                          }}
                        />
                      </div>
                    )}
                  </div>
                ) : (
                  <p>No chart data available</p>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default DatasetDetail;