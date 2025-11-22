"""
Scrape top holdings data from Groww mutual fund pages
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

# List of funds with their URLs
FUNDS = [
    {
        "fund_name": "UTI Large & Mid Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth"
    },
    {
        "fund_name": "UTI ELSS Tax Saver Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-long-term-equity-fund-tax-saving-direct-growth"
    },
    {
        "fund_name": "UTI Small Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-small-cap-fund-direct-growth"
    },
    {
        "fund_name": "UTI Mid Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-mid-cap-fund-direct-growth"
    },
    {
        "fund_name": "UTI Flexi Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-equity-fund-direct-growth"
    },
    {
        "fund_name": "UTI Value Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-value-fund-direct-growth"
    },
    {
        "fund_name": "UTI Healthcare Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-growth"
    },
    {
        "fund_name": "UTI Transportation and Logistics Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-transportation-and-logistics-fund-direct-growth"
    },
    {
        "fund_name": "UTI Banking and Financial Services Fund Direct Plan Growth",
        "url": "https://groww.in/mutual-funds/uti-banking-sector-fund-direct-growth"
    },
    {
        "fund_name": "UTI MNC Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-mnc-fund-direct-growth"
    },
    {
        "fund_name": "UTI India Consumer Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-india-lifestyle-fund-direct-growth"
    },
    {
        "fund_name": "UTI Nifty 50 Index Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-nifty-fund-direct-growth"
    },
    {
        "fund_name": "UTI Nifty Next 50 Index Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-nifty-next-50-index-fund-direct-growth"
    },
    {
        "fund_name": "UTI Infrastructure Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-infrastructure-fund-direct-growth"
    },
    {
        "fund_name": "UTI Innovation Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-innovation-fund-direct-growth"
    },
    {
        "fund_name": "UTI Multi Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-multi-cap-fund-direct-growth"
    },
    {
        "fund_name": "UTI Long Term Advantage Fund Series V Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-long-term-advantage-fund-series-v-direct-growth"
    },
    {
        "fund_name": "UTI Long Term Advantage Fund Series III Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-long-term-advantage-fund-series-iii-direct-growth"
    },
    {
        "fund_name": "UTI Gold ETF FoF Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-gold-etf-fof-direct-growth"
    },
    {
        "fund_name": "UTI Liquid Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-liquid-cash-plan-direct-growth"
    },
    {
        "fund_name": "UTI Money Market Fund Regular Plan Growth",
        "url": "https://groww.in/mutual-funds/uti-money-market-fund-regular-plan-growth"
    },
    {
        "fund_name": "UTI Healthcare Fund Direct IDCW",
        "url": "https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-dividend"
    },
    {
        "fund_name": "UTI Income Plus Arbitrage Active FoF Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-i-come-plus-arbitrage-active-fof-direct-growth"
    },
    {
        "fund_name": "UTI India Consumer Fund Direct IDCW",
        "url": "https://groww.in/mutual-funds/uti-india-lifestyle-fund-direct-dividend"
    },
    {
        "fund_name": "UTI Large & Mid Cap Fund Direct IDCW",
        "url": "https://groww.in/mutual-funds/uti-top-100-fund-direct-dividend"
    },
    {
        "fund_name": "UTI Large Cap Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-unit-scheme-1986-mastershare-direct-growth"
    },
    {
        "fund_name": "UTI Large Cap Fund Direct IDCW",
        "url": "https://groww.in/mutual-funds/uti-unit-scheme-1986-mastershare-direct-dividend"
    },
    {
        "fund_name": "UTI Liquid Cash Plan Direct IDCW Monthly",
        "url": "https://groww.in/mutual-funds/uti-liquid-cash-plan-direct-monthly-dividend"
    },
    {
        "fund_name": "UTI Long Duration Fund Direct IDCW Quarterly",
        "url": "https://groww.in/mutual-funds/uti-long-duration-fund-direct-idcw-quarterly"
    },
    {
        "fund_name": "UTI Monthly Income Scheme Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-monthly-i-come-scheme-direct-growth"
    },
    {
        "fund_name": "UTI Multi Asset Allocation Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-wealth-builder-fund-direct-growth"
    },
    {
        "fund_name": "UTI Multi Cap Fund (Ex) Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-multi-cap-fund-%28ex%29-direct-growth"
    },
    {
        "fund_name": "UTI Nifty 500 Value 50 Index Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-nifty-500-value-50-index-fund-direct-growth"
    },
    {
        "fund_name": "UTI Nifty Alpha Low Volatility 30 Index Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-nifty-alpha-low-volatility-30-index-fund-direct-growth"
    },
    {
        "fund_name": "UTI Nifty India Manufacturing Index Fund Direct Growth",
        "url": "https://groww.in/mutual-funds/uti-nifty-india-manufacturing-index-fund-direct-growth"
    }
]

def scrape_holdings(url):
    """Scrape top holdings from a Groww mutual fund page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        holdings = []
        
        # Try different selectors for holdings section
        # Method 1: Look for holdings table
        holdings_table = soup.find('table', {'class': lambda x: x and 'holdings' in x.lower()})
        if not holdings_table:
            # Try alternative selectors
            holdings_section = soup.find('div', {'id': lambda x: x and 'holdings' in x.lower()})
            if holdings_section:
                holdings_table = holdings_section.find('table')
        
        if holdings_table:
            rows = holdings_table.find_all('tr')
            for row in rows[1:6]:  # Get top 5 (skip header)
                cols = row.find_all('td')
                if len(cols) >= 4:  # Need at least 4 columns: Name, Sector, Instrument, Assets
                    stock_name = cols[0].get_text(strip=True)
                    percentage = cols[3].get_text(strip=True)  # Assets column (4th column)
                    
                    if stock_name and percentage:
                        holdings.append({
                            "stock": stock_name,
                            "percentage": percentage
                        })
        
        # Method 2: Look for holdings list items
        if not holdings:
            holdings_items = soup.find_all('div', {'class': lambda x: x and 'holding' in x.lower()})
            for item in holdings_items[:5]:
                stock = item.find('span', {'class': lambda x: x and 'name' in x.lower()})
                percent = item.find('span', {'class': lambda x: x and 'percent' in x.lower()})
                
                if stock and percent:
                    holdings.append({
                        "stock": stock.get_text(strip=True),
                        "percentage": percent.get_text(strip=True)
                    })
        
        return holdings
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def main():
    """Main function to scrape all funds and save to JSON"""
    all_holdings = []
    
    print("Starting to scrape holdings data...")
    print("=" * 60)
    
    for i, fund in enumerate(FUNDS, 1):
        print(f"\n{i}/{len(FUNDS)} Scraping: {fund['fund_name']}")
        print(f"URL: {fund['url']}")
        
        holdings = scrape_holdings(fund['url'])
        
        if holdings:
            print(f"✅ Found {len(holdings)} holdings")
            for h in holdings:
                print(f"   - {h['stock']}: {h['percentage']}")
            
            all_holdings.append({
                "fund_name": fund['fund_name'],
                "source_url": fund['url'],
                "chunk_type": "holdings_information",
                "data": {
                    "top_holdings": holdings
                }
            })
        else:
            print(f"❌ No holdings found")
        
        # Be respectful - wait between requests
        if i < len(FUNDS):
            time.sleep(2)
    
    # Save to file
    output_file = Path(__file__).parent.parent / 'rag_data' / 'scraped_holdings.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_holdings, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Scraping complete!")
    print(f"Scraped {len(all_holdings)} funds successfully")
    print(f"Saved to: {output_file}")
    print("\nNext steps:")
    print("1. Review scraped_holdings.json to verify the data")
    print("2. Manually merge this data into rag_chunks.json")
    print("3. Run regenerate_embeddings.py")

if __name__ == "__main__":
    main()
