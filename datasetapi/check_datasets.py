#!/usr/bin/env python3
"""
Check what datasets and summaries exist in the database
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'datasetapi.settings')
django.setup()

from datasets.models import Dataset, SummaryStatistics

def check_data():
    """Check what data exists"""
    
    print("DATASETS:")
    datasets = Dataset.objects.all()
    for dataset in datasets:
        print(f"  ID: {dataset.id}, Name: {dataset.name}, Processed: {dataset.is_processed}")
    
    print(f"\nTotal datasets: {len(datasets)}")
    
    print("\nSUMMARY STATISTICS:")
    summaries = SummaryStatistics.objects.all()
    for summary in summaries:
        print(f"  Dataset ID: {summary.dataset.id}, Records: {summary.total_records}")
        print(f"    Flowrate: {summary.avg_flowrate}")
        print(f"    Pressure: {summary.avg_pressure}")
        print(f"    Temperature: {summary.avg_temperature}")
        print(f"    Equipment: {summary.equipment_type_distribution}")
        print()
    
    print(f"Total summaries: {len(summaries)}")
    
    # Check which datasets don't have summaries
    dataset_ids_with_summaries = set(s.dataset.id for s in summaries)
    all_dataset_ids = set(d.id for d in datasets)
    missing_summaries = all_dataset_ids - dataset_ids_with_summaries
    
    if missing_summaries:
        print(f"\nDatasets WITHOUT summaries: {missing_summaries}")
    else:
        print("\nAll datasets have summaries")

if __name__ == "__main__":
    check_data()