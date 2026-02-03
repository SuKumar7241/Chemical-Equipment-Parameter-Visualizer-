# Equipment Data Analysis API - Complete Guide

## Overview

The Django backend has been extended with specialized APIs for equipment data analysis, focusing on:
- **CSV Upload with Validation**: Validates required columns for equipment data
- **Data Summary APIs**: Provides comprehensive analysis of flowrate, pressure, temperature, and equipment types
- **Pandas-based Analysis**: All data processing uses Pandas for robust statistical analysis
- **Clean JSON Responses**: Well-structured API responses with comprehensive error handling

## New API Endpoints

### 1. Equipment CSV Upload API
**Endpoint**: `POST /api/equipment/upload/`

**Purpose**: Upload and process equipment CSV files with strict validation

**Required CSV Columns** (case-insensitive):
- `equipment_id` (or `id`, `equipment_number`)
- `equipment_type` (or `type`, `category`, `equipment_category`)
- `flowrate` (or `flow_rate`, `flow`, `rate`)
- `pressure` (or `press`, `psi`, `bar`)
- `temperature` (or `temp`, `celsius`, `fahrenheit`)

**Optional CSV Columns**:
- `timestamp`, `location`, `status`, `operator`

**Request Format**:
```bash
POST /api/equipment/upload/
Content-Type: multipart/form-data

Form Data:
- file: [CSV file]
- name: "Equipment Dataset" (optional)
- description: "Description" (optional)
```

**Success Response (201)**:
```json
{
  "dataset_id": 4,
  "name": "Equipment Dataset",
  "status": "success",
  "message": "Equipment CSV uploaded and processed successfully",
  "summary": {
    "total_records": 10,
    "columns_processed": 7,
    "equipment_types_found": 4,
    "avg_flowrate": 127.74,
    "avg_pressure": 44.8,
    "avg_temperature": 83.25
  },
  "validation": {
    "is_valid": true,
    "column_mapping": {
      "equipment_id": "equipment_id",
      "equipment_type": "equipment_type",
      "flowrate": "flowrate",
      "pressure": "pressure",
      "temperature": "temperature"
    }
  },
  "data_quality": {
    "total_rows": 10,
    "complete_rows": 10,
    "missing_data_percentage": 0.0
  }
}
```

**Error Response (400)**:
```json
{
  "error": "CSV validation failed",
  "details": "Required column 'flowrate' not found. Expected one of: flowrate, flow_rate, flow, rate",
  "status": "validation_error"
}
```

### 2. Data Summary API
**Endpoints**: 
- `GET /api/equipment/summary/` - Combined summary of all datasets
- `GET /api/equipment/summary/{dataset_id}/` - Summary for specific dataset

**Purpose**: Get comprehensive analysis including total records, averages, and equipment distribution

**Response Format**:
```json
{
  "total_record_count": 10,
  "average_flowrate": 127.74,
  "average_pressure": 44.8,
  "average_temperature": 83.25,
  "equipment_type_distribution": {
    "Pump": 3,
    "Compressor": 3,
    "Valve": 2,
    "Heat Exchanger": 2
  },
  "operational_metrics": {
    "flowrate": {
      "average": 127.74,
      "median": 157.75,
      "std_deviation": 73.45,
      "min": 0.0,
      "max": 220.8,
      "count": 10,
      "missing_count": 0
    },
    "pressure": {
      "average": 44.8,
      "median": 46.6,
      "std_deviation": 14.23,
      "min": 25.0,
      "max": 65.2,
      "count": 10,
      "missing_count": 0
    },
    "temperature": {
      "average": 83.25,
      "median": 82.75,
      "std_deviation": 7.89,
      "min": 72.0,
      "max": 95.5,
      "count": 10,
      "missing_count": 0
    }
  },
  "data_quality": {
    "total_rows": 10,
    "complete_rows": 10,
    "missing_data_percentage": 0.0,
    "columns_with_missing_data": []
  },
  "equipment_analysis": {
    "total_equipment_types": 4,
    "equipment_type_distribution": {
      "Pump": 3,
      "Compressor": 3,
      "Valve": 2,
      "Heat Exchanger": 2
    },
    "most_common_equipment": "Pump",
    "equipment_type_percentages": {
      "Pump": 30.0,
      "Compressor": 30.0,
      "Valve": 20.0,
      "Heat Exchanger": 20.0
    }
  },
  "dataset_info": {
    "id": 4,
    "name": "Equipment Dataset",
    "description": "Test dataset for equipment API validation",
    "upload_date": "2026-01-26T19:06:45.123456Z",
    "total_rows": 10,
    "total_columns": 7
  },
  "analysis_timestamp": "2026-01-26T19:06:45.123456Z"
}
```

### 3. CSV Validation API
**Endpoint**: `POST /api/equipment/validate/`

**Purpose**: Validate CSV structure without uploading the file

**Request Format**:
```bash
POST /api/equipment/validate/
Content-Type: multipart/form-data

Form Data:
- file: [CSV file]
```

**Success Response (200)**:
```json
{
  "is_valid": true,
  "column_mapping": {
    "equipment_id": "equipment_id",
    "equipment_type": "equipment_type",
    "flowrate": "flowrate",
    "pressure": "pressure",
    "temperature": "temperature",
    "location": "location",
    "status": "status"
  },
  "missing_columns": [],
  "found_columns": ["equipment_id", "equipment_type", "flowrate", "pressure", "temperature", "location", "status"],
  "errors": [],
  "file_info": {
    "filename": "equipment_data.csv",
    "size": 1024,
    "rows": 10,
    "columns": 7
  },
  "data_preview": {
    "columns": ["equipment_id", "equipment_type", "flowrate", "pressure", "temperature", "location", "status"],
    "data": [
      {
        "equipment_id": "EQ001",
        "equipment_type": "Pump",
        "flowrate": 150.5,
        "pressure": 45.2,
        "temperature": 78.5,
        "location": "Plant A",
        "status": "Active"
      }
    ],
    "total_rows_shown": 5,
    "total_rows_in_dataset": 10
  }
}
```

### 4. Equipment Data Preview API
**Endpoint**: `GET /api/equipment/preview/{dataset_id}/`

**Purpose**: Get preview of processed equipment data

**Response Format**:
```json
{
  "dataset_info": {
    "id": 4,
    "name": "Equipment Dataset",
    "total_rows": 10,
    "total_columns": 7,
    "columns": ["equipment_id", "equipment_type", "flowrate", "pressure", "temperature", "location", "status"]
  },
  "column_types": {
    "equipment_id": "object",
    "equipment_type": "object",
    "flowrate": "float64",
    "pressure": "float64",
    "temperature": "float64",
    "location": "object",
    "status": "object"
  },
  "summary": {
    "avg_flowrate": 127.74,
    "avg_pressure": 44.8,
    "avg_temperature": 83.25,
    "equipment_types": ["Pump", "Compressor", "Valve", "Heat Exchanger"]
  }
}
```

## Testing the APIs

### Using PowerShell (Windows)

#### 1. Test CSV Validation
```powershell
# Create a test CSV file first
$csvContent = @"
equipment_id,equipment_type,flowrate,pressure,temperature
EQ001,Pump,150.5,45.2,78.5
EQ002,Compressor,200.0,60.8,85.2
"@
$csvContent | Out-File -FilePath "test_equipment.csv" -Encoding UTF8

# Validate the CSV
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/equipment/validate/" -Method POST -InFile "test_equipment.csv" -ContentType "multipart/form-data" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### 2. Upload Equipment CSV
```powershell
# Upload the CSV file
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/equipment/upload/" -Method POST -InFile "test_equipment.csv" -ContentType "multipart/form-data" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### 3. Get Data Summary
```powershell
# Get summary for all datasets
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/equipment/summary/" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10

# Get summary for specific dataset (replace 4 with actual dataset ID)
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/equipment/summary/4/" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

#### 4. Get Data Preview
```powershell
# Get data preview (replace 4 with actual dataset ID)
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/equipment/preview/4/" -UseBasicParsing
$response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Using Browser

You can test GET endpoints directly in your browser:
- http://127.0.0.1:8000/api/equipment/summary/
- http://127.0.0.1:8000/api/equipment/summary/4/
- http://127.0.0.1:8000/api/equipment/preview/4/

## Implementation Details

### Pandas Analysis Features

1. **Data Cleaning**:
   - Converts numeric columns with error handling
   - Removes negative flowrates (if invalid)
   - Standardizes equipment type names
   - Handles missing values gracefully

2. **Statistical Analysis**:
   - Mean, median, standard deviation
   - Min/max values
   - Count of valid/missing values
   - Percentile calculations

3. **Equipment Distribution**:
   - Count by equipment type
   - Percentage distribution
   - Most common equipment identification

4. **Data Quality Metrics**:
   - Missing data analysis
   - Complete vs incomplete records
   - Column-wise missing data counts

### Error Handling

1. **CSV Validation Errors**:
   - Missing required columns
   - Invalid file format
   - Empty files
   - Parsing errors

2. **Processing Errors**:
   - Data type conversion issues
   - Statistical calculation errors
   - Database save failures

3. **API Errors**:
   - File size limits
   - Invalid requests
   - Server errors

### Database Integration

1. **Enhanced Models**:
   - Added equipment-specific fields to SummaryStatistics
   - Quick access to operational metrics
   - Equipment type distribution storage

2. **Efficient Queries**:
   - Optimized for summary calculations
   - Combined dataset analysis
   - Fast retrieval of key metrics

## Key Features Delivered

**CSV Upload API with Validation**
- Accepts CSV files with required column validation
- Flexible column name matching (case-insensitive)
- Comprehensive error messages for missing columns

**Pandas-based Analysis**
- All data processing uses Pandas
- Robust statistical calculations
- Data cleaning and validation

**Data Summary API**
- Total record count
- Average flowrate, pressure, temperature
- Equipment type distribution with percentages
- Comprehensive operational metrics

**Clean JSON Responses**
- Well-structured response format
- Detailed error messages
- Comprehensive data quality metrics

**Graceful Error Handling**
- Invalid CSV format handling
- Missing column validation
- Data processing error recovery
- User-friendly error messages

## Production Ready

The equipment APIs are production-ready with:
- Input validation and sanitization
- Comprehensive error handling
- Efficient database operations
- Scalable architecture
- Clean separation of concerns

The APIs provide exactly what was requested: specialized endpoints for equipment data with focus on operational metrics and robust CSV processing using Pandas.