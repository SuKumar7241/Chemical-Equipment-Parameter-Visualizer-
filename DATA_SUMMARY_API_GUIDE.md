# Data Summary API Guide

## Overview

The Data Summary API provides comprehensive data summaries using Pandas calculations. It returns total record counts, average values for key metrics, and equipment type distributions from uploaded CSV datasets.

## API Endpoints

### 1. Get Specific Dataset Summary

**Endpoint:** `GET /api/data-summary/{dataset_id}/`

**Description:** Returns detailed summary for a specific dataset

**Parameters:**
- `dataset_id` (integer): The ID of the dataset to summarize

**Response Format:**
```json
{
  "total_records": 1500,
  "averages": {
    "flowrate": 45.67,
    "pressure": 120.34,
    "temperature": 78.92
  },
  "equipment_type_distribution": {
    "Pump": 450,
    "Valve": 320,
    "Sensor": 280,
    "Controller": 250,
    "Motor": 200
  }
}
```

### 2. List All Dataset Summaries

**Endpoint:** `GET /api/data-summaries/`

**Description:** Returns summaries for all processed datasets

**Response Format:**
```json
{
  "count": 3,
  "summaries": [
    {
      "dataset_id": 1,
      "dataset_name": "Equipment Data 2024",
      "total_records": 1500,
      "averages": {
        "flowrate": 45.67,
        "pressure": 120.34,
        "temperature": 78.92
      },
      "equipment_type_distribution": {
        "Pump": 450,
        "Valve": 320,
        "Sensor": 280
      },
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Data Calculations

### 1. Total Record Count
- **Method:** `len(df)` using Pandas
- **Description:** Total number of rows in the dataset
- **Type:** Integer

### 2. Average Values
Calculated for three key metrics using Pandas:

#### Flowrate
- **Column Names Searched:** `flowrate`, `flow_rate`, `flow`, `rate` (case-insensitive)
- **Calculation:** `df[column].mean()` with `pd.to_numeric()` conversion
- **Handling:** Invalid values converted to NaN and excluded from calculation
- **Type:** Float (rounded to 2 decimal places) or `null`

#### Pressure
- **Column Names Searched:** `pressure`, `press`, `psi`, `bar` (case-insensitive)
- **Calculation:** `df[column].mean()` with `pd.to_numeric()` conversion
- **Handling:** Invalid values converted to NaN and excluded from calculation
- **Type:** Float (rounded to 2 decimal places) or `null`

#### Temperature
- **Column Names Searched:** `temperature`, `temp`, `celsius`, `fahrenheit` (case-insensitive)
- **Calculation:** `df[column].mean()` with `pd.to_numeric()` conversion
- **Handling:** Invalid values converted to NaN and excluded from calculation
- **Type:** Float (rounded to 2 decimal places) or `null`

### 3. Equipment Type Distribution
- **Column Names Searched:** `equipment_type`, `equipment`, `type`, `device_type`, `machine_type` (case-insensitive)
- **Calculation:** `df[column].value_counts()` using Pandas
- **Handling:** NaN values excluded from counts
- **Type:** Dictionary with equipment type as key and count as value

## Error Handling

### Graceful Column Handling
- If target columns don't exist, values are set to `null`
- Case-insensitive column name matching
- Multiple possible column names for each metric
- Invalid data converted to NaN and excluded

### API Error Responses

#### Dataset Not Found (404)
```json
{
  "error": "Dataset not found",
  "message": "Dataset with ID 123 does not exist"
}
```

#### Dataset Not Processed (400)
```json
{
  "error": "Dataset not yet processed",
  "message": "Please wait for dataset processing to complete"
}
```

#### File Not Found (404)
```json
{
  "error": "Dataset file not found",
  "message": "The original CSV file is no longer available"
}
```

#### CSV Read Error (500)
```json
{
  "error": "Failed to read CSV file",
  "message": "Error details here"
}
```

## Implementation Details

### Technology Stack
- **Framework:** Django REST Framework
- **Data Processing:** Pandas
- **Database:** Django ORM with SummaryStatistics model
- **Serialization:** Custom DataSummarySerializer

### Data Storage
- Results are stored in the `SummaryStatistics` model
- Cached for performance (updated when recalculated)
- Linked to original dataset via foreign key

### Performance Considerations
- CSV files are read using `pd.read_csv()` for optimal performance
- Results are cached in database to avoid recalculation
- Graceful handling of large datasets

## Testing

### Test Script
Run the test script to validate API functionality:

```bash
python datasetapi/test_data_summary_api.py
```

### Manual Testing

#### 1. Test with curl
```bash
# Get specific dataset summary
curl -X GET http://localhost:8000/api/data-summary/1/

# Get all dataset summaries
curl -X GET http://localhost:8000/api/data-summaries/
```

#### 2. Test with Python requests
```python
import requests

# Test specific dataset
response = requests.get('http://localhost:8000/api/data-summary/1/')
print(response.json())

# Test all summaries
response = requests.get('http://localhost:8000/api/data-summaries/')
print(response.json())
```

## Integration Examples

### Frontend Integration
```javascript
// Fetch dataset summary
async function getDatasetSummary(datasetId) {
  const response = await fetch(`/api/data-summary/${datasetId}/`);
  const data = await response.json();
  
  console.log('Total Records:', data.total_records);
  console.log('Average Flowrate:', data.averages.flowrate);
  console.log('Equipment Distribution:', data.equipment_type_distribution);
}
```

### Desktop App Integration
```python
import requests

def get_dataset_summary(dataset_id):
    response = requests.get(f'http://localhost:8000/api/data-summary/{dataset_id}/')
    if response.status_code == 200:
        return response.json()
    return None

# Usage
summary = get_dataset_summary(1)
if summary:
    print(f"Total records: {summary['total_records']}")
    print(f"Average pressure: {summary['averages']['pressure']}")
```

## Requirements Compliance

### ✅ Requirements Met
1. **Total record count** - Calculated using `len(df)`
2. **Average values for flowrate, pressure, temperature** - Calculated using Pandas `mean()`
3. **Equipment type distribution** - Calculated using Pandas `value_counts()`
4. **All calculations using Pandas** - All data processing uses Pandas functions
5. **Data from uploaded CSV** - Reads original CSV files using `pd.read_csv()`
6. **Results stored and retrievable** - Cached in SummaryStatistics model
7. **Clean, structured JSON** - Well-formatted API responses
8. **Graceful handling** - Missing/invalid columns handled properly

### ✅ Restrictions Followed
- **No extra metrics** - Only required metrics included
- **No hardcoded values** - All values calculated from actual data
- **No modification of existing APIs** - New endpoints added without changing existing ones

## API Documentation Summary

The Data Summary API provides exactly what was requested:
- **Endpoint:** `/api/data-summary/{dataset_id}/`
- **Method:** GET
- **Response:** JSON with total_records, averages, and equipment_type_distribution
- **Technology:** Django REST Framework + Pandas
- **Error Handling:** Comprehensive error responses
- **Performance:** Cached results with database storage