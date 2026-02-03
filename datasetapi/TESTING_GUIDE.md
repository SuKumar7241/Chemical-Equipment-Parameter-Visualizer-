# Testing Guide - Dataset Analysis API

This guide shows how to test the Django backend with the sample equipment data.

## Quick Start

### 1. Download Sample Data
Download the sample equipment data from: https://drive.google.com/file/d/1cq26Jb7vQ8RC1POISdGic0jr_tuTJI1E/view

Save it as `sample_equipment_data.csv` in the `datasetapi` directory.

### 2. Run Demo Script
```bash
cd datasetapi
python demo_upload.py
```

### 3. Start Django Server
```bash
python manage.py runserver
```

### 4. Test API Endpoints
The server will be available at `http://localhost:8000/`

## API Testing Examples

### 1. Upload Dataset via API
```bash
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -F "file=@sample_equipment_data.csv" \
  -F "name=Equipment Dataset" \
  -F "description=Sample equipment data for testing"
```

### 2. List All Datasets
```bash
curl http://localhost:8000/api/datasets/
```

### 3. Get Dataset Details
```bash
curl http://localhost:8000/api/datasets/1/
```

### 4. Get Dataset Statistics
```bash
curl http://localhost:8000/api/datasets/1/statistics/
```

### 5. Get Column Information
```bash
curl http://localhost:8000/api/datasets/1/columns/
```

### 6. Get Numeric Statistics Only
```bash
curl http://localhost:8000/api/statistics/1/numeric_summary/
```

### 7. Get Categorical Statistics Only
```bash
curl http://localhost:8000/api/statistics/1/categorical_summary/
```

## Expected API Responses

### Dataset List Response
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Equipment Dataset",
      "description": "Sample equipment data for testing",
      "file_name": "sample_equipment_data.csv",
      "file_size": 2048,
      "file_type": "csv",
      "upload_date": "2026-01-26T10:30:00Z",
      "total_rows": 100,
      "total_columns": 8,
      "is_processed": true
    }
  ]
}
```

### Statistics Response Structure
```json
{
  "id": 1,
  "statistics_data": {
    "dataset_info": {
      "total_rows": 100,
      "total_columns": 8,
      "memory_usage": 6400,
      "missing_values_total": 5
    },
    "columns": {
      "equipment_id": {
        "name": "equipment_id",
        "type": "int64",
        "count": 100,
        "missing_count": 0,
        "unique_count": 100,
        "mean": 50.5,
        "median": 50.5,
        "std": 29.01,
        "min": 1,
        "max": 100
      }
    }
  },
  "numeric_columns_count": 4,
  "categorical_columns_count": 4,
  "missing_values_count": 5
}
```

## Testing with Python Requests

Create a test script to interact with the API:

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api"

# Upload a dataset
def upload_dataset():
    with open('sample_equipment_data.csv', 'rb') as f:
        files = {'file': f}
        data = {
            'name': 'Equipment Dataset',
            'description': 'Sample equipment data'
        }
        response = requests.post(f"{BASE_URL}/datasets/upload/", files=files, data=data)
        return response.json()

# Get dataset list
def get_datasets():
    response = requests.get(f"{BASE_URL}/datasets/")
    return response.json()

# Get dataset statistics
def get_statistics(dataset_id):
    response = requests.get(f"{BASE_URL}/datasets/{dataset_id}/statistics/")
    return response.json()

# Run tests
if __name__ == "__main__":
    # Upload dataset
    dataset = upload_dataset()
    print("Dataset uploaded:", dataset['id'])
    
    # Get statistics
    stats = get_statistics(dataset['id'])
    print("Statistics generated for", stats['numeric_columns_count'], "numeric columns")
```

## Admin Interface Testing

1. Create superuser:
```bash
python manage.py createsuperuser
```

2. Visit admin interface:
```
http://localhost:8000/admin/
```

3. Navigate through:
   - Datasets → View uploaded datasets
   - Summary Statistics → View statistical analysis
   - Dataset Columns → View column-level details

## Troubleshooting

### Common Issues

1. **File not found error**
   - Ensure `sample_equipment_data.csv` is in the `datasetapi` directory
   - Check file permissions

2. **Import errors**
   - Run `pip install -r requirements.txt`
   - Ensure you're in the correct directory

3. **Database errors**
   - Run `python manage.py migrate`
   - Delete `db.sqlite3` and run migrations again if needed

4. **Server not starting**
   - Check if port 8000 is available
   - Use `python manage.py runserver 8001` for different port

### Validation

The API includes validation for:
- File size (max 10MB)
- File types (CSV, JSON, Excel)
- Required fields
- Data processing errors

### Performance Notes

- Processing time depends on dataset size
- Large files may take longer to analyze
- Statistics are cached in the database
- Memory usage scales with dataset size

## Next Steps

After successful testing:
1. Try uploading different file formats (JSON, Excel)
2. Test with larger datasets
3. Explore the admin interface
4. Build a frontend application using these APIs
5. Add authentication and user management