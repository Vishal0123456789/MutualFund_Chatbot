"""
Merge real scraped data into both rag_chunks.json and rag_chunks.csv
Updates expense_ratio, fund_manager, and fund_size with real Groww data
"""
import json
import csv
from pathlib import Path
from datetime import datetime

# Paths
RAG_DATA_DIR = Path(__file__).parent.parent / 'rag_data'
RAG_CHUNKS_JSON = RAG_DATA_DIR / 'rag_chunks.json'
RAG_CHUNKS_CSV = RAG_DATA_DIR / 'rag_chunks.csv'

SCRAPED_NAV_FILE = RAG_DATA_DIR / 'scraped_nav.json'
SCRAPED_EXPENSE_RATIO_FILE = RAG_DATA_DIR / 'scraped_expense_ratio.json'
SCRAPED_FUND_MANAGERS_FILE = RAG_DATA_DIR / 'scraped_fund_managers.json'
SCRAPED_FUND_SIZE_FILE = RAG_DATA_DIR / 'scraped_fund_size.json'

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filepath, data):
    """Save JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_csv(filepath):
    """Load CSV file"""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def save_csv(filepath, rows):
    """Save CSV file"""
    if not rows:
        return
    
    fieldnames = ['Chunk Type', 'Fund Name', 'Source URL', 'Data']
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def merge_data():
    """Merge all scraped data into JSON and CSV"""
    
    print("Loading data files...")
    
    # Load all scraped data
    nav_data = load_json(SCRAPED_NAV_FILE)
    expense_data = load_json(SCRAPED_EXPENSE_RATIO_FILE)
    manager_data = load_json(SCRAPED_FUND_MANAGERS_FILE)
    size_data = load_json(SCRAPED_FUND_SIZE_FILE)
    
    # Load JSON chunks
    chunks = load_json(RAG_CHUNKS_JSON)
    print(f"Loaded chunks from rag_chunks.json (dict with {len(chunks)} types)")
    
    # Load CSV rows
    csv_rows = load_csv(RAG_CHUNKS_CSV)
    print(f"Loaded {len(csv_rows)} rows from rag_chunks.csv")
    
    # Create lookup dictionaries by URL
    nav_by_url = {item['url']: item for item in nav_data}
    expense_by_url = {item['url']: item for item in expense_data}
    manager_by_url = {item['url']: item for item in manager_data}
    size_by_url = {item['url']: item for item in size_data}
    
    # Track updates
    updates = {
        'nav_updated': 0,
        'expense_updated': 0,
        'manager_updated': 0,
        'size_updated': 0,
        'chunks_processed': 0
    }
    
    print("\nMerging scraped data into JSON chunks...")
    
    # Process each chunk type
    for chunk_type_key, chunk_list in chunks.items():
        for chunk in chunk_list:
            updates['chunks_processed'] += 1
            source_url = chunk.get('source_url', '')
            chunk_type = chunk.get('chunk_type', '')
            
            # Update expense_information chunks
            if chunk_type == 'expense_information' and source_url in expense_by_url:
                expense_item = expense_by_url[source_url]
                if expense_item.get('expense_ratio'):
                    chunk['expense_ratio'] = expense_item['expense_ratio']
                    chunk['stamp_duty'] = expense_item.get('stamp_duty', '0.005%')
                    chunk['data_source'] = 'Groww (Scraped 2025-11-23)'
                    updates['expense_updated'] += 1
            
            # Update nav_sip_information chunks
            if chunk_type == 'nav_sip_information' and source_url in nav_by_url:
                nav_item = nav_by_url[source_url]
                if nav_item.get('nav'):
                    chunk['nav'] = nav_item['nav']
                    chunk['nav_date'] = nav_item.get('nav_date')
                    chunk['data_source'] = 'Groww (Scraped 2025-11-23)'
                    updates['nav_updated'] = updates.get('nav_updated', 0) + 1
            
            # Update fund_characteristics chunks
            if chunk_type == 'fund_characteristics' and source_url in (manager_by_url or size_by_url):
                if source_url in manager_by_url:
                    manager_item = manager_by_url[source_url]
                    if manager_item.get('fund_manager'):
                        chunk['fund_manager'] = manager_item['fund_manager']
                        chunk['data_source'] = 'Groww (Scraped 2025-11-23)'
                        updates['manager_updated'] += 1
                
                if source_url in size_by_url:
                    size_item = size_by_url[source_url]
                    if size_item.get('fund_size'):
                        chunk['fund_size'] = size_item['fund_size']
                        chunk['data_source'] = 'Groww (Scraped 2025-11-23)'
                        updates['size_updated'] += 1
    
    # Save updated JSON chunks
    print("Saving updated JSON chunks...")
    save_json(RAG_CHUNKS_JSON, chunks)
    
    # Update CSV rows
    print("\nMerging scraped data into CSV rows...")
    
    for row in csv_rows:
        source_url = row.get('Source URL', '')
        chunk_type = row.get('Chunk Type', '')
        
        # Parse data JSON
        try:
            data = json.loads(row['Data'])
        except json.JSONDecodeError:
            continue
        
        # Update expense information
        if chunk_type == 'expense_information' and source_url in expense_by_url:
            expense_item = expense_by_url[source_url]
            if expense_item.get('expense_ratio'):
                data['expense_ratio'] = expense_item['expense_ratio']
                data['stamp_duty'] = expense_item.get('stamp_duty', '0.005%')
                row['Data'] = json.dumps(data, ensure_ascii=False)
        
        # Update fund characteristics
        if chunk_type == 'fund_characteristics':
            if source_url in manager_by_url:
                manager_item = manager_by_url[source_url]
                if manager_item.get('fund_manager'):
                    data['fund_manager'] = manager_item['fund_manager']
                    row['Data'] = json.dumps(data, ensure_ascii=False)
            
            if source_url in size_by_url:
                size_item = size_by_url[source_url]
                if size_item.get('fund_size'):
                    data['fund_size'] = size_item['fund_size']
                    row['Data'] = json.dumps(data, ensure_ascii=False)
    
    # Save updated CSV
    print("Saving updated CSV...")
    save_csv(RAG_CHUNKS_CSV, csv_rows)
    
    print("\n" + "=" * 70)
    print("Data Merge Complete!")
    print("=" * 70)
    print(f"\nMerge Summary:")
    print(f"  Total chunks processed: {updates['chunks_processed']}")
    print(f"  NAV values updated: {updates.get('nav_updated', 0)}")
    print(f"  Expense Ratio updated: {updates['expense_updated']}")
    print(f"  Fund Manager updated: {updates['manager_updated']}")
    print(f"  Fund Size updated: {updates['size_updated']}")
    print(f"\nFiles updated:")
    print(f"  {RAG_CHUNKS_JSON}")
    print(f"  {RAG_CHUNKS_CSV}")
    print(f"\nNext step: Run regenerate_embeddings.py to update embeddings")

if __name__ == "__main__":
    merge_data()
