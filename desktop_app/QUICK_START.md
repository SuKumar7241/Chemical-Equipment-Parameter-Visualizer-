# Quick Start Guide - Desktop Application

## Enhanced Version Available!

The desktop application now has an **Enhanced Version** with professional UI, interactive charts, and advanced features.

## Prerequisites Check

**Python 3.7+** - Check with: `python --version`
**Django Backend Running** - Must be running on http://localhost:8000
**Dependencies Installed** - PyQt5, matplotlib, requests, numpy

## Installation Steps

1. **Navigate to desktop app directory:**
   ```bash
   cd desktop_app
   ```

2. **Install dependencies (if not already done):**
   ```bash
   pip install PyQt5 matplotlib requests numpy pandas
   ```

## Running the Application

### Step 1: Start Django Backend
```bash
# In the datasetapi directory
cd datasetapi
python manage.py runserver
```
Keep this terminal open - the backend must stay running.

### Step 2: Choose Your Version

#### Enhanced Version (Recommended)
```bash
# Professional UI with charts and advanced features
cd desktop_app
python enhanced_app.py
```

#### Basic Version
```bash
# Simple, functional interface
cd desktop_app
python fixed_app.py
```

#### Batch Launcher (Windows)
```bash
# Auto-checks dependencies and launches enhanced version
cd desktop_app
.\run_enhanced.bat
```

## Enhanced Version Features

### Professional Interface
- **Styled Login** - Professional header design with branding
- **Statistics Dashboard** - Visual cards showing key metrics
- **Enhanced Upload** - Drag-drop styling with file size display
- **Interactive Charts** - Matplotlib integration with 4-chart analysis
- **Paginated History** - Professional table with navigation

### Data Visualization
- **Data Type Distribution** - Pie chart showing column types
- **Missing Values Analysis** - Bar chart of null counts per column
- **Numeric Statistics** - Bar chart of mean values
- **Dataset Summary** - Overview statistics visualization

### Advanced Functionality
- **Dataset Selector** - Dialog for choosing datasets to analyze
- **Real-time Updates** - Charts update when data changes
- **Professional Styling** - CSS-based UI with hover effects
- **Responsive Threading** - Smooth UI with background operations

## Version Comparison

| Feature | Basic Version | Enhanced Version |
|---------|---------------|------------------|
| Login Interface | Simple form | Professional styled |
| Dashboard | Basic table | Statistics cards + table |
| Upload | File selection | Enhanced drag-drop |
| Data Visualization | None | Full matplotlib suite |
| Dataset Analysis | Basic info | Interactive charts |
| History View | Simple list | Paginated with details |
| UI Styling | Minimal | Professional CSS |

**Recommendation:** Use the Enhanced Version for the complete experience!

1. **Login Window will appear**
   - If you have an account: Use the Login tab
   - If you're new: Use the Register tab to create an account

2. **Register New User:**
   - Username: Choose any username
   - Email: Enter your email
   - Password: Choose a secure password
   - Confirm Password: Re-enter the same password
   - Click "Register"

3. **Login Existing User:**
   - Username: Your existing username
   - Password: Your password
   - Click "Login"

## Using the Application

### Dashboard Tab
- View statistics overview
- See recent datasets
- Quick access to key metrics

### Upload Tab
- Drag and drop CSV files
- Or click to browse for files
- Add optional name and description
- Click "Upload Dataset"

### Datasets Tab
- View all your datasets in a table
- Click on a dataset to see details
- View interactive charts and statistics
- Delete datasets if needed

### History Tab
- Browse all datasets with pagination
- View storage overview
- See cleanup status
- Delete datasets from history

## Troubleshooting

### Application Won't Start
```bash
# Check if all dependencies are installed
python -c "import PyQt5, matplotlib, requests, pandas, numpy; print('All dependencies OK')"
```

### Can't Connect to Backend
- Ensure Django server is running: http://localhost:8000
- Check if you can access http://localhost:8000/api/ in your browser
- Verify no firewall is blocking the connection

### Login Issues
- Make sure you're using the correct credentials
- Try registering a new account if login fails
- Check the Django backend logs for authentication errors

### Charts Not Showing
- First run of matplotlib may take time to build font cache
- Ensure dataset is fully processed (status shows "Processed")
- Check that statistics data is available

### File Upload Issues
- Only CSV files are supported
- Check file permissions
- Ensure file size is reasonable (< 100MB recommended)
- Verify Django backend is accepting uploads

## Features Overview

### Authentication
- JWT token-based authentication
- Persistent login (remembers you between sessions)
- Secure token storage

### File Upload
- Drag and drop interface
- Progress tracking
- File validation
- Metadata input (name, description)

### Data Visualization
- Bar charts for numeric data
- Pie charts for data type distribution
- Missing values analysis
- Summary statistics

### Dataset Management
- Complete dataset listing
- Detailed dataset information
- Interactive charts
- Delete functionality

### History Management
- Paginated dataset history
- Storage overview
- Cleanup status monitoring
- Bulk operations

## Tips for Best Experience

1. **Keep Backend Running**: Always ensure the Django backend is running before starting the desktop app

2. **File Formats**: Only upload CSV files with proper headers in the first row

3. **Processing Time**: Large files may take time to process - wait for "Processed" status

4. **Memory Usage**: Close the application when not in use to free memory

5. **Updates**: Refresh data using the "Refresh" buttons to see latest changes

## Common Workflows

### Upload and Analyze Dataset
1. Go to Upload tab
2. Drag/drop or select CSV file
3. Add name and description (optional)
4. Click "Upload Dataset"
5. Go to Datasets tab to view analysis
6. Click on your dataset to see charts

### View Dataset History
1. Go to History tab
2. Browse datasets with pagination
3. View storage statistics
4. Delete old datasets if needed

### Manage Datasets
1. Go to Datasets tab
2. Select a dataset from the table
3. View details and charts on the right
4. Delete datasets using "Delete Selected"

## Support

If you encounter issues:
1. Check that all prerequisites are met
2. Verify Django backend is running and accessible
3. Check console output for error messages
4. Ensure all dependencies are properly installed

The desktop application provides the same functionality as the web interface but with a native desktop experience!