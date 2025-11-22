"""
Scrape exit load data from Groww mutual fund pages
"""
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

def scrape_exit_load(url):
    """Scrape exit load from a Groww mutual fund page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find exit load information
        # Method 1: Look for "Exit load" text
        exit_load_text = None
        
        # Search for text containing "exit load"
        for text_element in soup.find_all(text=True):
            text_lower = text_element.lower().strip()
            if 'exit load' in text_lower:
                # Get the parent and try to find the value
                parent = text_element.parent
                if parent:
                    # Try to get the next sibling or nearby text
                    siblings = list(parent.next_siblings)
                    for sibling in siblings[:3]:
                        if sibling and hasattr(sibling, 'get_text'):
                            sibling_text = sibling.get_text(strip=True)
                            if sibling_text and len(sibling_text) > 0:
                                exit_load_text = sibling_text
                                break
                    
                    # If not found in siblings, check parent's text
                    if not exit_load_text:
                        parent_text = parent.get_text(strip=True)
                        if 'exit load' in parent_text.lower():
                            # Extract just the exit load part
                            parts = parent_text.split('Exit load')
                            if len(parts) > 1:
                                exit_load_text = 'Exit load' + parts[1].strip()
                                # Clean up if too long
                                if len(exit_load_text) > 100:
                                    exit_load_text = exit_load_text[:100]
                                break
        
        # Method 2: Look in tables
        if not exit_load_text:
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    for i, col in enumerate(cols):
                        if 'exit load' in col.get_text(strip=True).lower():
                            # Next column should have the value
                            if i + 1 < len(cols):
                                exit_load_text = cols[i + 1].get_text(strip=True)
                                break
                    if exit_load_text:
                        break
                if exit_load_text:
                    break
        
        return exit_load_text if exit_load_text else None
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    """Main function to scrape all funds and update exit loads"""
    # Load existing RAG chunks
    rag_file = Path(__file__).parent.parent / 'rag_data' / 'rag_chunks.json'
    with open(rag_file, 'r', encoding='utf-8') as f:
        rag_data = json.load(f)
    
    print("Starting to scrape exit loads...")
    print("=" * 60)
    
    updated_count = 0
    total_count = len(rag_data['expense_information'])
    
    for i, chunk in enumerate(rag_data['expense_information'], 1):
        fund_name = chunk['fund_name']
        url = chunk['source_url']
        
        print(f"\n{i}/{total_count} Scraping: {fund_name}")
        print(f"URL: {url}")
        
        exit_load = scrape_exit_load(url)
        
        if exit_load:
            print(f"✅ Found exit load: {exit_load}")
            chunk['data']['exit_load'] = exit_load
            updated_count += 1
        else:
            print(f"❌ No exit load found")
        
        # Be respectful - wait between requests
        if i < total_count:
            import time
            time.sleep(2)
    
    # Save updated data
    with open(rag_file, 'w', encoding='utf-8') as f:
        json.dump(rag_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Scraping complete!")
    print(f"Updated {updated_count}/{total_count} funds with exit load data")
    print(f"Saved to: {rag_file}")
    print("\nNext steps:")
    print("1. Review rag_chunks.json to verify the exit load data")
    print("2. Run regenerate_embeddings.py")
    print("3. Restart the backend")

if __name__ == "__main__":
    main()
