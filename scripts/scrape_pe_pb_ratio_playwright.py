"""
P/E and P/B Ratio scraper using Playwright
Extracts ratios from Holdings/Portfolio section after scrolling
"""
import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright

# List of all 35 UTI funds with their correct Groww URLs
UTI_FUNDS = {
    "UTI Large & Mid Cap Fund Direct Growth": "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth",
    "UTI ELSS Tax Saver Fund Direct Growth": "https://groww.in/mutual-funds/uti-long-term-equity-fund-tax-saving-direct-growth",
    "UTI Gold ETF FoF Direct Growth": "https://groww.in/mutual-funds/uti-gold-etf-fof-direct-growth",
    "UTI Transportation and Logistics Fund Direct Growth": "https://groww.in/mutual-funds/uti-transportation-and-logistics-fund-direct-growth",
    "UTI Healthcare Fund Direct Growth": "https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-growth",
    "UTI Small Cap Fund Direct Growth": "https://groww.in/mutual-funds/uti-small-cap-fund-direct-growth",
    "UTI Value Fund Direct Growth": "https://groww.in/mutual-funds/uti-value-fund-direct-growth",
    "UTI Mid Cap Fund Direct Growth": "https://groww.in/mutual-funds/uti-mid-cap-fund-direct-growth",
    "UTI Nifty Next 50 Index Fund Direct Growth": "https://groww.in/mutual-funds/uti-nifty-next-50-index-fund-direct-growth",
    "UTI Banking and Financial Services Fund Direct Plan Growth": "https://groww.in/mutual-funds/uti-banking-sector-fund-direct-growth",
    "UTI Nifty 50 Index Fund Direct Growth": "https://groww.in/mutual-funds/uti-nifty-fund-direct-growth",
    "UTI Flexi Cap Fund Direct Growth": "https://groww.in/mutual-funds/uti-equity-fund-direct-growth",
    "UTI Money Market Fund Regular Plan Growth": "https://groww.in/mutual-funds/uti-money-market-fund-regular-plan-growth",
    "UTI Liquid Direct Growth": "https://groww.in/mutual-funds/uti-liquid-cash-plan-direct-growth",
    "UTI MNC Fund Direct Growth": "https://groww.in/mutual-funds/uti-mnc-fund-direct-growth",
    "UTI India Consumer Fund Direct Growth": "https://groww.in/mutual-funds/uti-india-lifestyle-fund-direct-growth",
    "UTI Long Term Advantage Fund Series III Direct Growth": "https://groww.in/mutual-funds/uti-long-term-advantage-fund-series-iii-direct-growth",
    "UTI Healthcare Fund Direct IDCW": "https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-dividend",
    "UTI Income Plus Arbitrage Active FoF Direct Growth": "https://groww.in/mutual-funds/uti-i-come-plus-arbitrage-active-fof-direct-growth",
    "UTI India Consumer Fund Direct IDCW": "https://groww.in/mutual-funds/uti-india-lifestyle-fund-direct-dividend",
    "UTI Infrastructure Fund Direct Growth": "https://groww.in/mutual-funds/uti-infrastructure-fund-direct-growth",
    "UTI Innovation Fund Direct Growth": "https://groww.in/mutual-funds/uti-innovation-fund-direct-growth",
    "UTI Large & Mid Cap Fund Direct IDCW": "https://groww.in/mutual-funds/uti-top-100-fund-direct-dividend",
    "UTI Large Cap Fund Direct Growth": "https://groww.in/mutual-funds/uti-unit-scheme-1986-mastershare-direct-growth",
    "UTI Large Cap Fund Direct IDCW": "https://groww.in/mutual-funds/uti-unit-scheme-1986-mastershare-direct-dividend",
    "UTI Liquid Cash Plan Direct IDCW Monthly": "https://groww.in/mutual-funds/uti-liquid-cash-plan-direct-monthly-dividend",
    "UTI Long Duration Fund Direct IDCW Quarterly": "https://groww.in/mutual-funds/uti-long-duration-fund-direct-idcw-quarterly",
    "UTI Long Term Advantage Fund Series V Direct Growth": "https://groww.in/mutual-funds/uti-long-term-advantage-fund-series-v-direct-growth",
    "UTI Monthly Income Scheme Direct Growth": "https://groww.in/mutual-funds/uti-monthly-i-come-scheme-direct-growth",
    "UTI Multi Asset Allocation Fund Direct Growth": "https://groww.in/mutual-funds/uti-wealth-builder-fund-direct-growth",
    "UTI Multi Cap Fund (Ex) Direct Growth": "https://groww.in/mutual-funds/uti-multi-cap-fund-%28ex%29-direct-growth",
    "UTI Multi Cap Fund Direct Growth": "https://groww.in/mutual-funds/uti-multi-cap-fund-direct-growth",
    "UTI Nifty 500 Value 50 Index Fund Direct Growth": "https://groww.in/mutual-funds/uti-nifty-500-value-50-index-fund-direct-growth",
    "UTI Nifty Alpha Low Volatility 30 Index Fund Direct Growth": "https://groww.in/mutual-funds/uti-nifty-alpha-low-volatility-30-index-fund-direct-growth",
    "UTI Nifty India Manufacturing Index Fund Direct Growth": "https://groww.in/mutual-funds/uti-nifty-india-manufacturing-index-fund-direct-growth"
}

async def scrape_pe_pb_ratios(page, url, fund_name):
    """Scrape P/E and P/B ratios from Holdings/Portfolio section"""
    try:
        await page.goto(url, wait_until='load')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)
        
        pe_ratio = "NA"
        pb_ratio = "NA"
        
        # Scroll slowly to load Holdings/Portfolio section
        # Scroll multiple times to ensure all content loads
        for scroll_count in range(5):
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await page.wait_for_timeout(800)
        
        # Get full page content
        page_content = await page.content()
        page_text = await page.inner_text('body')
        
        # Strategy 1: Look for "P/E Ratio" or "PE Ratio" patterns in text
        # Try multiple patterns to match different formats
        pe_patterns = [
            r'P/E\s+Ratio\s*:?\s*([0-9]+\.[0-9]{2})',
            r'PE\s+Ratio\s*:?\s*([0-9]+\.[0-9]{2})',
            r'Price\s+to\s+Earnings\s*:?\s*([0-9]+\.[0-9]{2})',
            r'P/E\s*:?\s*([0-9]+\.[0-9]{2})',
            r'PE\s*:?\s*([0-9]+\.[0-9]{2})'
        ]
        
        for pattern in pe_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 0 < val < 500:  # Reasonable P/E range
                        pe_ratio = val
                        break
                except:
                    pass
        
        # Strategy 2: Look for "P/B Ratio" or "PB Ratio" patterns
        pb_patterns = [
            r'P/B\s+Ratio\s*:?\s*([0-9]+\.[0-9]{2})',
            r'PB\s+Ratio\s*:?\s*([0-9]+\.[0-9]{2})',
            r'Price\s+to\s+Book\s*:?\s*([0-9]+\.[0-9]{2})',
            r'P/B\s*:?\s*([0-9]+\.[0-9]{2})',
            r'PB\s*:?\s*([0-9]+\.[0-9]{2})'
        ]
        
        for pattern in pb_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                try:
                    val = float(match.group(1))
                    if 0 < val < 500:  # Reasonable P/B range
                        pb_ratio = val
                        break
                except:
                    pass
        
        # Strategy 3: Look for data-testid attributes containing "pe" or "pb"
        try:
            pe_elements = await page.query_selector_all('div[data-testid*="pe"], span[data-testid*="pe"]')
            if pe_elements and pe_ratio == "NA":
                for elem in pe_elements[:5]:
                    text = await elem.inner_text()
                    numbers = re.findall(r'([0-9]+\.[0-9]{2})', text)
                    if numbers:
                        try:
                            val = float(numbers[0])
                            if 0 < val < 500:
                                pe_ratio = val
                                break
                        except:
                            pass
        except:
            pass
        
        # Strategy 4: Search in HTML structure for P/E near numbers
        if pe_ratio == "NA":
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                if 'p/e' in line.lower() or 'pe' in line.lower():
                    # Look in this line and next 2 lines for numbers
                    for j in range(i, min(i + 3, len(lines))):
                        numbers = re.findall(r'([0-9]+\.[0-9]{2})', lines[j])
                        if numbers:
                            try:
                                val = float(numbers[0])
                                if 0 < val < 500:
                                    pe_ratio = val
                                    break
                            except:
                                pass
                    if pe_ratio != "NA":
                        break
        
        return {
            'url': url,
            'fund_name': fund_name,
            'pe_ratio': pe_ratio,
            'pb_ratio': pb_ratio
        }
    
    except Exception as e:
        print(f"  Error: {fund_name}: {str(e)}")
        return {
            'url': url,
            'fund_name': fund_name,
            'pe_ratio': "NA",
            'pb_ratio': "NA"
        }

async def main():
    """Main scraping function"""
    print("Scraping P/E and P/B Ratio data for all 35 UTI funds...")
    print("=" * 70)
    
    ratio_data = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        for i, (fund_name, url) in enumerate(UTI_FUNDS.items(), 1):
            print(f"{i}/35 - {fund_name}")
            
            page = await browser.new_page()
            page.set_default_navigation_timeout(30000)
            page.set_default_timeout(30000)
            
            result = await scrape_pe_pb_ratios(page, url, fund_name)
            ratio_data.append(result)
            
            pe_str = f"{result['pe_ratio']}" if result['pe_ratio'] != "NA" else "NA"
            pb_str = f"{result['pb_ratio']}" if result['pb_ratio'] != "NA" else "NA"
            print(f"  ✓ P/E: {pe_str}, P/B: {pb_str}")
            
            await page.close()
        
        await browser.close()
    
    # Save to JSON
    output_path = Path(__file__).parent.parent / 'rag_data' / 'scraped_pe_pb_ratios_all_35.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ratio_data, f, indent=2, ensure_ascii=False)
    
    # Summary
    with_pe = sum(1 for item in ratio_data if item['pe_ratio'] != "NA")
    with_pb = sum(1 for item in ratio_data if item['pb_ratio'] != "NA")
    print("\n" + "=" * 70)
    print(f"✅ Scraping complete!")
    print(f"Successfully extracted P/E ratio: {with_pe}/{len(ratio_data)}")
    print(f"Successfully extracted P/B ratio: {with_pb}/{len(ratio_data)}")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
