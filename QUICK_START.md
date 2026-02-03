# Quick Start Guide

## Django Server is Running!

Your Django backend is now running at: **http://127.0.0.1:8000/**

## How to Test the API

### 1. Download Sample Equipment Data
- Go to: https://drive.google.com/file/d/1cq26Jb7vQ8RC1POISdGic0jr_tuTJI1E/view
- Download the CSV file
- Save it as `sample_equipment_data.csv` in the `datasetapi` directory

### 2. Test API Endpoints

**Open a new terminal/command prompt** (keep the server running) and try these:

#### List all datasets:
```bash
curl http://127.0.0.1:8000/api/datasets/
```

#### Upload the sample equipment data:
```bash
curl -X POST http://127.0.0.1:8000/api/datasets/upload/ -F "file=@sample_equipment_data.csv" -F "name=Equipment Dataset" -F "description=Sample equipment data"
```

#### Get dataset details (replace {id} with actual ID from upload response):
```bash
curl http://127.0.0.1:8000/api/datasets/1/
```

#### Get statistics:
```bash
curl http://127.0.0.1:8000/api/datasets/1/statistics/
```

#### Get column information:
```bash
curl http://127.0.0.1:8000/api/datasets/1/columns/
```

### 3. Access Django Admin (Optional)

1. **Create superuser** (in a new terminal):
   ```bash
   cd datasetapi
   python manage.py createsuperuser
   ```

2. **Visit admin interface**:
   - Go to: http://127.0.0.1:8000/admin/
   - Login with your superuser credentials
   - Explore the datasets, statistics, and columns

### 4. Test with Browser

You can also test some endpoints directly in your browser:
- http://127.0.0.1:8000/api/datasets/ - List datasets
- http://127.0.0.1:8000/api/datasets/1/ - View dataset details
- http://127.0.0.1:8000/admin/ - Admin interface

## Current Status

**Django server running** at http://127.0.0.1:8000/
**Database created** with sample data
**API endpoints ready** for testing
**Models working** correctly

## File Locations

- **Main project**: `datasetapi/`
- **Django files**: `datasetapi/datasetapi/`
- **App files**: `datasetapi/datasets/`
- **Database**: `datasetapi/db.sqlite3`

## Next Steps

1. Download the sample equipment CSV from the Google Drive link
2. Test the upload endpoint with curl or a tool like Postman
3. Explore the generated statistics
4. Build a frontend that uses these API endpoints

## To Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## To Restart

```bash
cd datasetapi
python manage.py runserver
```

Your Django backend is fully functional and ready for use!