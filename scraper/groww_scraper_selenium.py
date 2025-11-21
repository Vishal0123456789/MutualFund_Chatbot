"""
Groww Mutual Fund Scheme Scraper using Selenium
For JavaScript-rendered pages
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, Optional
from urllib.parse import urlparse
import validators

from scraper.groww_scraper import GrowwScraper


class GrowwScraperSelenium(GrowwScraper):
    """Selenium-based scraper for JavaScript-rendered Groww pages"""
    
    def __init__(self, headless: bool = True):
        super().__init__()
        self.headless = headless
        self.driver = None
    
    def _setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def fetch_page(self, url: str, save_html: bool = False) -> Optional[BeautifulSoup]:
        """Fetch and parse the webpage using Selenium"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        try:
            if self.driver is None:
                self._setup_driver()
            
            print(f"Loading page: {url}")
            self.driver.get(url)
            
            # Wait for page to load - look for common elements
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                # Additional wait for dynamic content
                time.sleep(3)
            except Exception as e:
                print(f"Warning: Timeout waiting for page load: {e}")
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            
            # Save HTML for debugging if requested
            if save_html:
                import os
                os.makedirs('data/raw_html', exist_ok=True)
                filename = url.split('/')[-1] + '_selenium.html'
                with open(f'data/raw_html/{filename}', 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(page_source)
                print(f"Saved HTML to data/raw_html/{filename}")
            
            return BeautifulSoup(page_source, 'lxml')
            
        except Exception as e:
            raise Exception(f"Failed to fetch page with Selenium: {str(e)}")
    
    def extract_fund_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund name with enhanced selectors"""
        try:
            # Try multiple selectors for fund name
            selectors = [
                'h1',
                '[data-testid="fund-name"]',
                '.fund-name',
                'h1[class*="fund"]',
                '[class*="fundName"]',
                '[class*="FundName"]',
                'h1[class*="title"]',
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5 and 'UTI' in text.upper():
                        return text
            
            # Look in meta tags
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title_text = og_title.get('content')
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
                return title_text.strip()
            
            # Look for title tag
            title = soup.find('title')
            if title:
                title_text = title.get_text(strip=True)
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
                return title_text
            
            return None
        except Exception as e:
            print(f"Error extracting fund name: {e}")
            return None
    
    def extract_nav(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract NAV with enhanced parsing"""
        try:
            # Get all text content
            text = soup.get_text()
            
            # Look for NAV patterns
            nav_patterns = [
                r'NAV[:\s]*₹\s*([\d,]+\.?\d*)\s*\(as of\s*([^)]+)\)',
                r'₹\s*([\d,]+\.?\d*)\s*\(as of\s*([^)]+)\)',
                r'NAV[:\s]*₹\s*([\d,]+\.?\d*)',
            ]
            
            for pattern in nav_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nav_value = match.group(1).replace(',', '')
                    date = match.group(2) if len(match.groups()) > 1 else None
                    return {
                        'value': nav_value,
                        'date': date.strip() if date else None
                    }
            
            return None
        except Exception as e:
            print(f"Error extracting NAV: {e}")
            return None
    
    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

