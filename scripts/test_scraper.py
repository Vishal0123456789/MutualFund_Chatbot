"""
Test script for Groww scraper
Tests scraping with the provided example URL
"""

import sys
import os
import json
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.groww_scraper import GrowwScraper
from scraper.groww_scraper_playwright import GrowwScraperPlaywright
from scraper.validators import DataValidator
from database.db_manager import DatabaseManager


def test_scraper(url: str, use_playwright: bool = True):
    """Test the scraper with a given URL"""
    print(f"\n{'='*60}")
    print(f"Testing scraper with URL: {url}")
    print(f"Using Playwright: {use_playwright}")
    print(f"{'='*60}\n")
    
    # Initialize scraper
    if use_playwright:
        scraper = GrowwScraperPlaywright(headless=True)
    else:
        scraper = GrowwScraper()
    
    # Validate URL
    if not scraper.validate_url(url):
        print(f"[ERROR] Invalid URL: {url}")
        return
    
    print("[OK] URL validated")
    
    # Scrape data
    try:
        print("\n[INFO] Fetching page...")
        data = scraper.scrape_scheme(url, save_html=True)  # Save HTML for debugging
        
        print("\n[INFO] Scraped Data:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Validate data
        print("\n[INFO] Validating data...")
        validator = DataValidator()
        validation_result = validator.validate_scraped_data(data)
        
        print(f"\nValidation Status: {'[OK] Valid' if validation_result['is_valid'] else '[WARNING] Has Issues'}")
        
        if validation_result['errors']:
            print("\n[ERROR] Errors:")
            for error in validation_result['errors']:
                print(f"  - {error}")
        
        if validation_result['warnings']:
            print("\n[WARNING] Warnings:")
            for warning in validation_result['warnings']:
                print(f"  - {warning}")
        
        # Save to database
        print("\n[INFO] Saving to database...")
        os.makedirs('data', exist_ok=True)
        db_manager = DatabaseManager('data/mutual_funds.db')
        scheme_id = db_manager.save_scheme_data(data, validation_result)
        
        if scheme_id:
            print(f"[OK] Data saved successfully! Scheme ID: {scheme_id}")
        else:
            print("[ERROR] Failed to save data to database")
        
        # Verify saved data
        print("\n[INFO] Verifying saved data...")
        saved_data = db_manager.get_scheme_data(url)
        if saved_data:
            print(f"[OK] Data retrieved from database:")
            print(f"   Scheme: {saved_data['scheme_name']}")
            print(f"   Data points: {len(saved_data['data'])}")
        
    except Exception as e:
        print(f"\n[ERROR] Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Close Playwright browser if used
        if use_playwright and hasattr(scraper, 'close'):
            scraper.close()


if __name__ == "__main__":
    # Test URL from user
    test_url = "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth"
    use_playwright = True
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    if len(sys.argv) > 2:
        use_playwright = sys.argv[2].lower() == 'true'
    
    test_scraper(test_url, use_playwright=use_playwright)

