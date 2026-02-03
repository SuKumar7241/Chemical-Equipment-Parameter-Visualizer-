# Dataset Analyzer Desktop Application

A PyQt5 desktop application that consumes the Django REST API for dataset analysis. This application provides a native desktop interface for uploading CSV files, viewing data analysis, and managing datasets.

## Features

- **Authentication**: User login and registration with JWT tokens
- **CSV Upload**: Drag-and-drop file upload with progress tracking
- **Data Visualization**: Interactive charts using Matplotlib
- **Dataset Management**: View, analyze, and delete datasets
- **History Tracking**: Paginated dataset history with statistics
- **Table View**: Comprehensive data table display
- **Real-time Updates**: Automatic refresh across tabs

## Prerequisites

- Python 3.7 or higher
- Django backend running on `http://localhost:8000`
- Required Python packages (see requirements.txt)

## Installation

1. **Navigate to the desktop app directory:**
   ```bash
   cd desktop_app
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Ensure the Django backend is running:**
   ```bash
   # In the datasetapi directory
   python manage.py runserver
   ```

2. **Start the desktop application:**
   
   **Option A - Fixed Version (Recommended)**:
   ```bash
   python complete_app_no_matplotlib.py
   # OR on Windows:
   run_fixed_app.bat
   ```
   
   **Option B - Original Version**:
   ```bash
   python main.py
   ```

3. **First-time setup:**
   - Register a new account or login with existing credentials
   - Upload your first CSV dataset
   - Explore the dashboard and analytics features

## Version Information

### Fixed Version (`complete_app_no_matplotlib.py`)
- **Recommended for Windows users**
- Removes matplotlib integration to avoid Qt5 backend hanging issues
- Provides text-based data analysis instead of charts
- More stable and faster startup
- All other features remain the same

### Original Version (`main.py`)
- Full matplotlib chart integration
- May experience hanging issues on some Windows systems
- Complete visualization features

## Application Structure

```
desktop_app/
- main.py                 # Application entry point
- requirements.txt        # Python dependencies
- services/              # API communication services
  - __init__.py
  - api_client.py      # HTTP client for REST API
  - auth_service.py    # Authentication management
  - dataset_service.py # Dataset operations
- ui/                    # User interface components
  - __init__.py
  - login_window.py    # Login/registration window
  - main_window.py     # Main application window
  - dashboard_tab.py   # Dashboard with statistics
  - upload_tab.py      # File upload interface
  - datasets_tab.py    # Dataset management with charts
  - history_tab.py     # Dataset history with pagination
```

## Features Overview

### Authentication Window
- **Login Tab**: Username/password authentication
- **Register Tab**: New user registration
- **Token Management**: Automatic JWT token handling
- **Persistent Login**: Remembers authentication between sessions

### Dashboard Tab
- **Statistics Overview**: Total datasets, processed count, rows, columns
- **Recent Datasets**: Last 5 uploaded datasets
- **Quick Stats**: Visual stat cards with color coding
- **Auto-refresh**: Updates when datasets change

### Upload Tab
- **Drag-and-Drop**: Intuitive file selection
- **File Validation**: CSV format checking
- **Progress Tracking**: Upload progress indication
- **Metadata Input**: Optional name and description
- **Guidelines**: Built-in upload instructions

### Datasets Tab
- **Table View**: Comprehensive dataset listing
- **Dataset Details**: Overview with statistics
- **Interactive Charts**: Matplotlib visualizations
  - Numeric column means (bar chart)
  - Data type distribution (pie chart)
  - Missing values analysis (bar chart)
  - Dataset summary statistics
- **Delete Functionality**: Remove datasets with confirmation

### History Tab
- **Paginated History**: Browse all datasets with pagination
- **Storage Overview**: Statistics cards showing usage
- **Cleanup Status**: Information about automatic cleanup
- **Detailed Table**: Complete dataset information
- **Bulk Operations**: Delete datasets from history

## Charts and Visualizations

The application uses Matplotlib to create various charts:

1. **Numeric Column Means**: Bar chart showing average values
2. **Data Type Distribution**: Pie chart of column data types
3. **Missing Values**: Bar chart of null counts per column
4. **Summary Statistics**: Bar chart of key dataset metrics

## API Integration

The desktop app consumes the same Django REST APIs as the web frontend:

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/status/` - Authentication status

### Dataset Endpoints
- `GET /api/datasets/` - List datasets
- `POST /api/datasets/upload/` - Upload dataset
- `GET /api/datasets/{id}/` - Dataset details
- `GET /api/datasets/{id}/statistics/` - Dataset statistics
- `GET /api/datasets/{id}/columns/` - Dataset columns
- `DELETE /api/datasets/{id}/delete_dataset/` - Delete dataset

### History Endpoints
- `GET /api/history/datasets/` - Paginated history
- `GET /api/history/status/` - History status
- `DELETE /api/history/datasets/{id}/` - Delete from history

## Configuration

### API URL Configuration
The application defaults to `http://localhost:8000`. To change this, modify the `base_url` parameter in `services/api_client.py`:

```python
class APIClient:
    def __init__(self, base_url: str = "http://your-api-server:8000"):
```

### Authentication Token Storage
Authentication tokens are stored in `~/.dataset_analyzer_token` for persistent login.

## Error Handling

The application includes comprehensive error handling:

- **Network Errors**: Connection failures and timeouts
- **API Errors**: Server-side error responses
- **File Errors**: Invalid file formats and access issues
- **Authentication Errors**: Token expiration and invalid credentials

## Threading

The application uses QThread for background operations to prevent UI blocking:

- **Authentication**: Login/register operations
- **File Upload**: Dataset upload with progress
- **Data Loading**: API calls for datasets and statistics
- **Chart Generation**: Matplotlib chart creation

## Styling

The application uses a modern, professional design:

- **Color Scheme**: Blue (#3498db), Green (#27ae60), Red (#e74c3c), Orange (#f39c12)
- **Typography**: Arial font family with appropriate sizing
- **Layout**: Card-based design with proper spacing
- **Responsive**: Adapts to different window sizes

## Troubleshooting

### Common Issues

1. **Application Won't Start**
   - Check Python version (3.7+)
   - Verify all dependencies are installed
   - Ensure PyQt5 is properly installed

2. **Cannot Connect to API**
   - Verify Django backend is running on port 8000
   - Check firewall settings
   - Confirm API URL configuration

3. **Authentication Issues**
   - Delete `~/.dataset_analyzer_token` file
   - Check backend authentication endpoints
   - Verify user credentials

4. **Charts Not Displaying**
   - Ensure matplotlib is installed
   - Check dataset processing status
   - Verify statistics data availability

5. **File Upload Problems**
   - Confirm file is CSV format
   - Check file permissions
   - Verify backend upload endpoint

### Development Tips

- Use Qt Designer for UI modifications
- Enable debug logging for API calls
- Test with various CSV file formats
- Monitor memory usage with large datasets

## Performance Considerations

- **Large Files**: Upload progress indication for large CSV files
- **Memory Usage**: Efficient data handling for large datasets
- **UI Responsiveness**: Background threading for all API calls
- **Chart Rendering**: Optimized matplotlib figure generation

## Security Features

- **Token Storage**: Secure local token storage
- **HTTPS Support**: Ready for HTTPS API endpoints
- **Input Validation**: File format and size validation
- **Error Sanitization**: Safe error message display

## Future Enhancements

Potential improvements for future versions:

- **Export Functionality**: Export charts and reports
- **Advanced Filtering**: Dataset filtering and search
- **Batch Operations**: Multiple file upload
- **Custom Charts**: User-defined chart types
- **Data Preview**: Sample data display before upload
- **Settings Panel**: User preferences and configuration

## License

This desktop application is part of the Dataset Analyzer project suite.