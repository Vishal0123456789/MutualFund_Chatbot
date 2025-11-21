"""
Script to prepare scraped data for RAG system by chunking related information together
while maintaining source URL associations.
"""

import sys
import json
import csv
from pathlib import Path
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager


def prepare_rag_chunks():
    """Prepare data chunks for RAG system"""
    print("Preparing data for RAG system...")
    
    # Initialize database manager
    db_manager = DatabaseManager('data/mutual_funds.db')
    
    # Get all schemes
    schemes = db_manager.get_all_schemes()
    
    if not schemes:
        print("No schemes found in database!")
        return
    
    print(f"Processing {len(schemes)} schemes...")
    
    # Define chunk categories
    chunk_categories = {
        'expense_information': ['expense_ratio', 'exit_load', 'min_sip', 'stamp_duty'],
        'performance_metrics': ['fund_returns', 'category_averages', 'rank', 'pe_ratio', 'pb_ratio', 'annualised_returns'],
        'fund_characteristics': ['fund_size', 'fund_manager', 'lock_in', 'scheme_type', 'sub_category', 'is_elss', 'category_label'],
        'risk_information': ['riskometer', 'risk_metrics', 'benchmark'],
        'platform_information': ['statement_download_info']
    }
    
    # Store chunks by category
    chunks = defaultdict(list)
    
    # Process each scheme
    for scheme in schemes:
        scheme_data = db_manager.get_scheme_data(scheme['source_url'])
        if not scheme_data:
            continue
            
        fund_name = scheme_data['scheme_name']
        source_url = scheme_data['source_url']
        data = scheme_data['data']
        
        print(f"Processing: {fund_name}")
        
        # Create chunks for each category
        for category, data_types in chunk_categories.items():
            # Collect relevant data points for this category
            category_data = {}
            for data_type in data_types:
                if data_type in data and data[data_type]:
                    category_data[data_type] = data[data_type]
            
            # Only create chunk if we have data
            if category_data:
                chunk = {
                    'fund_name': fund_name,
                    'source_url': source_url,
                    'chunk_type': category,
                    'data': category_data
                }
                chunks[category].append(chunk)
    
    # Handle platform information separately (not tied to specific funds)
    platform_chunks = []
    for scheme in schemes:
        if 'help' in scheme['source_url'] or 'transaction-history' in scheme['source_url']:
            scheme_data = db_manager.get_scheme_data(scheme['source_url'])
            if scheme_data and scheme_data['data']:
                chunk = {
                    'fund_name': 'Groww Platform',
                    'source_url': scheme['source_url'],
                    'chunk_type': 'platform_information',
                    'data': scheme_data['data']
                }
                platform_chunks.append(chunk)
    
    if platform_chunks:
        chunks['platform_information'].extend(platform_chunks)
    
    # Save chunks to files
    output_dir = Path('rag_data')
    output_dir.mkdir(exist_ok=True)
    
    # Save as JSON
    json_file = output_dir / 'rag_chunks.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(dict(chunks), f, indent=2, ensure_ascii=False)
    
    print(f"Saved JSON chunks to {json_file}")
    
    # Save as CSV for easier inspection
    csv_file = output_dir / 'rag_chunks.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Chunk Type', 'Fund Name', 'Source URL', 'Data'])
        
        for category, category_chunks in chunks.items():
            for chunk in category_chunks:
                # Convert data to string for CSV
                data_str = json.dumps(chunk['data'], ensure_ascii=False)
                writer.writerow([
                    chunk['chunk_type'],
                    chunk['fund_name'],
                    chunk['source_url'],
                    data_str
                ])
    
    print(f"Saved CSV chunks to {csv_file}")
    
    # Print summary
    print("\nRAG Data Preparation Summary:")
    print("=" * 40)
    total_chunks = 0
    for category, category_chunks in chunks.items():
        print(f"{category}: {len(category_chunks)} chunks")
        total_chunks += len(category_chunks)
    print(f"Total chunks: {total_chunks}")
    
    # Show sample chunks
    print("\nSample chunks:")
    print("-" * 20)
    for category, category_chunks in list(chunks.items())[:2]:
        if category_chunks:
            chunk = category_chunks[0]
            print(f"\nCategory: {chunk['chunk_type']}")
            print(f"Fund: {chunk['fund_name']}")
            print("Data:")
            for key, value in list(chunk['data'].items())[:3]:  # Show first 3 items
                print(f"  {key}: {value}")


if __name__ == "__main__":
    prepare_rag_chunks()