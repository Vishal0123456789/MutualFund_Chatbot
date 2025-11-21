"""
Script to scrape multiple UTI mutual fund schemes
"""

import sys
import os
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.groww_scraper_playwright import GrowwScraperPlaywright
from scraper.validators import DataValidator
from database.db_manager import DatabaseManager


# List of UTI scheme URLs to scrape
UTI_SCHEME_URLS = [
    "https://groww.in/mutual-funds/uti-gold-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/uti-transportation-and-logistics-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-value-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-nifty-next-50-index-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-banking-sector-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-nifty-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-money-market-fund-regular-plan-growth",
    "https://groww.in/mutual-funds/uti-liquid-cash-plan-direct-growth",
    "https://groww.in/mutual-funds/uti-mnc-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-india-lifestyle-fund-direct-growth",
    "https://groww.in/mutual-funds/uti-long-term-equity-fund-tax-saving-direct-growth",
    "https://groww.in/mutual-funds/uti-long-term-advantage-fund-series-iii-direct-growth",
]


def scrape_all_schemes(urls: list, delay: float = 2.0):
    """
    Scrape all schemes from the provided URLs
    Args:
        urls: List of scheme URLs
        delay: Delay between requests in seconds
    """
    print(f"\n{'='*60}")
    print(f"Starting batch scraping of {len(urls)} schemes")
    print(f"{'='*60}\n")
    
    scraper = GrowwScraperPlaywright(headless=True)
    validator = DataValidator()
    os.makedirs('data', exist_ok=True)
    db_manager = DatabaseManager('data/mutual_funds.db')
    
    results = {
        'success': [],
        'failed': [],
        'partial': []
    }
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing: {url}")
        print("-" * 60)
        
        try:
            # Validate URL
            if not scraper.validate_url(url):
                print(f"❌ Invalid URL: {url}")
                results['failed'].append({'url': url, 'error': 'Invalid URL'})
                continue
            
            # Scrape data
            data = scraper.scrape_scheme(url)
            
            # Validate data
            validation_result = validator.validate_scraped_data(data)
            
            # Save to database
            scheme_id = db_manager.save_scheme_data(data, validation_result)
            
            if scheme_id:
                status = 'success' if validation_result['is_valid'] else 'partial'
                if validation_result['errors']:
                    status = 'failed'
                
                results[status].append({
                    'url': url,
                    'scheme_name': data.get('fund_name'),
                    'scheme_id': scheme_id,
                    'errors': validation_result.get('errors', []),
                    'warnings': validation_result.get('warnings', [])
                })
                
                print(f"✅ Scraped: {data.get('fund_name', 'Unknown')}")
                if validation_result['warnings']:
                    print(f"⚠️  Warnings: {len(validation_result['warnings'])}")
            else:
                results['failed'].append({'url': url, 'error': 'Database save failed'})
                print(f"❌ Failed to save to database")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results['failed'].append({'url': url, 'error': str(e)})
        finally:
            # Close browser after each scrape to avoid memory issues
            if hasattr(scraper, 'close'):
                scraper.close()
        
        # Delay between requests to be respectful
        if i < len(urls):
            time.sleep(delay)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Scraping Summary")
    print(f"{'='*60}")
    print(f"✅ Successfully scraped: {len(results['success'])}")
    print(f"⚠️  Partially scraped: {len(results['partial'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed URLs:")
        for item in results['failed']:
            print(f"  - {item['url']}: {item.get('error', 'Unknown error')}")
    
    return results


if __name__ == "__main__":
    # Use provided URLs or command line arguments
    urls_to_scrape = UTI_SCHEME_URLS
    
    if len(sys.argv) > 1:
        # Read URLs from file or command line
        if os.path.isfile(sys.argv[1]):
            with open(sys.argv[1], 'r') as f:
                urls_to_scrape = [line.strip() for line in f if line.strip()]
        else:
            urls_to_scrape = sys.argv[1:]
    
    scrape_all_schemes(urls_to_scrape, delay=2.0)

