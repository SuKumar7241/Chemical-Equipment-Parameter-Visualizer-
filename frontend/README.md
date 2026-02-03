# Dataset Analyzer Frontend

A React.js frontend application for the Dataset Analyzer API. This application provides a user-friendly interface for uploading CSV files, viewing data analysis, and managing datasets.

## Features

- **Authentication**: User registration and login with JWT tokens
- **CSV Upload**: Drag-and-drop file upload with progress tracking
- **Data Visualization**: Interactive charts using Chart.js
- **Dataset Management**: View, analyze, and delete datasets
- **History Tracking**: Browse dataset history with pagination
- **Responsive Design**: Mobile-friendly interface

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn package manager
- Backend API running on `http://localhost:8000`

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure API URL (optional):**
   
   The app is configured to use `http://localhost:8000` as the backend URL by default. If your backend runs on a different port, create a `.env` file:
   
   ```bash
   echo "REACT_APP_API_URL=http://localhost:8000" > .env
   ```

## Running the Application

1. **Start the development server:**
   ```bash
   npm start
   ```

2. **Open your browser:**
   
   The application will automatically open at `http://localhost:3000`

3. **First-time setup:**
   - Register a new account or login with existing credentials
   - Upload your first CSV dataset
   - Explore the dashboard and analytics features

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - Ejects from Create React App (irreversible)

## Application Structure

```
src/
- components/          # React components
  - Dashboard.js     # Main dashboard with stats
  - Upload.js        # File upload interface
  - DatasetList.js   # Dataset listing
  - DatasetDetail.js # Dataset details with charts
  - History.js       # Dataset history with pagination
  - Login.js         # User authentication
  - Register.js      # User registration
  - Navbar.js        # Navigation component
- contexts/            # React contexts
  - AuthContext.js   # Authentication state management
- services/            # API services
  - api.js           # Axios configuration and interceptors
- App.js               # Main application component
- index.js             # Application entry point
- index.css            # Global styles
```

## API Integration

The frontend consumes the following backend endpoints:

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/status/` - Check authentication status

### Dataset Management
- `GET /api/datasets/` - List all datasets
- `POST /api/datasets/upload/` - Upload new dataset
- `GET /api/datasets/{id}/` - Get dataset details
- `GET /api/datasets/{id}/statistics/` - Get dataset statistics
- `GET /api/datasets/{id}/columns/` - Get dataset columns
- `DELETE /api/datasets/{id}/delete_dataset/` - Delete dataset

### History Management
- `GET /api/history/datasets/` - Get paginated dataset history
- `GET /api/history/status/` - Get history status and cleanup info
- `DELETE /api/history/datasets/{id}/` - Delete specific dataset

## Features Overview

### Dashboard
- Overview statistics (total datasets, processed datasets, total rows)
- Recent datasets table
- Quick action buttons

### Upload
- Drag-and-drop file upload
- File validation (CSV only)
- Upload progress tracking
- Automatic redirect to dataset details

### Dataset List
- Tabular view of all datasets
- Sorting and filtering capabilities
- Quick actions (view, delete)

### Dataset Detail
- Comprehensive dataset information
- Interactive charts and visualizations
- Column analysis
- Statistics overview

### History
- Paginated dataset history
- Storage overview
- Cleanup status information
- Bulk operations

### Charts and Visualizations
- Bar charts for numeric data means
- Pie charts for data type distribution
- Equipment-specific statistics
- Responsive chart containers

## Styling

The application uses a custom CSS framework with:
- Responsive grid system
- Card-based layout
- Professional color scheme
- Mobile-first design
- Accessible form controls

## Error Handling

- Comprehensive error boundaries
- API error handling with user-friendly messages
- Loading states for all async operations
- Form validation and feedback

## Security Features

- JWT token-based authentication
- Automatic token refresh
- Protected routes
- CSRF protection via API configuration

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on `http://localhost:8000`
   - Check CORS configuration in Django settings
   - Verify API endpoints are accessible

2. **Authentication Issues**
   - Clear browser localStorage
   - Check JWT token expiration
   - Verify backend authentication endpoints

3. **File Upload Problems**
   - Ensure file is CSV format
   - Check file size limits
   - Verify multipart form data handling

4. **Charts Not Displaying**
   - Check if dataset is processed
   - Verify Chart.js dependencies
   - Ensure statistics data is available

### Development Tips

- Use browser developer tools for debugging
- Check network tab for API requests
- Monitor console for JavaScript errors
- Use React Developer Tools extension

## Production Build

To create a production build:

```bash
npm run build
```

This creates a `build` folder with optimized files ready for deployment.

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Maintain consistent code formatting
4. Add proper error handling
5. Write meaningful commit messages

## License

This project is part of the Dataset Analyzer application suite.