import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Upload = () => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    file: null
  });
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [dragOver, setDragOver] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    if (e.target.name === 'file') {
      setFormData({
        ...formData,
        file: e.target.files[0]
      });
    } else {
      setFormData({
        ...formData,
        [e.target.name]: e.target.value
      });
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setFormData({
          ...formData,
          file: file,
          name: formData.name || file.name.replace('.csv', '')
        });
      } else {
        setError('Please upload a CSV file');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.file) {
      setError('Please select a file to upload');
      return;
    }

    if (!formData.file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setUploading(true);

    try {
      const uploadData = new FormData();
      uploadData.append('file', formData.file);
      uploadData.append('name', formData.name || formData.file.name.replace('.csv', ''));
      if (formData.description) {
        uploadData.append('description', formData.description);
      }

      const response = await api.post('/api/datasets/upload/', uploadData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setSuccess('Dataset uploaded successfully!');
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        file: null
      });
      
      // Redirect to dataset detail page after a short delay
      setTimeout(() => {
        navigate(`/datasets/${response.data.id}`);
      }, 2000);

    } catch (err) {
      console.error('Upload error:', err);
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h1>Upload Dataset</h1>
      
      <div className="card">
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Dataset Name</label>
            <input
              type="text"
              id="name"
              name="name"
              className="form-control"
              value={formData.name}
              onChange={handleChange}
              placeholder="Enter dataset name (optional)"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              className="form-control"
              rows="3"
              value={formData.description}
              onChange={handleChange}
              placeholder="Enter dataset description (optional)"
            />
          </div>
          
          <div className="form-group">
            <label>CSV File</label>
            <div 
              className={`upload-area ${dragOver ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              {formData.file ? (
                <div>
                  <p><strong>Selected file:</strong> {formData.file.name}</p>
                  <p><strong>Size:</strong> {(formData.file.size / 1024 / 1024).toFixed(2)} MB</p>
                  <button 
                    type="button" 
                    onClick={() => setFormData({...formData, file: null})}
                    className="btn btn-secondary"
                  >
                    Remove File
                  </button>
                </div>
              ) : (
                <div>
                  <p>Drag and drop your CSV file here, or</p>
                  <input
                    type="file"
                    id="file"
                    name="file"
                    accept=".csv"
                    onChange={handleChange}
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="file" className="btn btn-primary">
                    Choose File
                  </label>
                </div>
              )}
            </div>
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={uploading || !formData.file}
          >
            {uploading ? 'Uploading...' : 'Upload Dataset'}
          </button>
        </form>
      </div>
      
      <div className="card">
        <h3>Upload Guidelines</h3>
        <ul>
          <li>Only CSV files are supported</li>
          <li>Maximum file size: 100MB</li>
          <li>First row should contain column headers</li>
          <li>Data will be automatically processed and analyzed</li>
          <li>You can view statistics and charts after processing</li>
        </ul>
      </div>
    </div>
  );
};

export default Upload;