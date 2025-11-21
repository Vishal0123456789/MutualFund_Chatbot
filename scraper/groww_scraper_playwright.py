"""
Groww Mutual Fund Scheme Scraper using Playwright
For JavaScript-rendered pages - more reliable than Selenium
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, Optional
from urllib.parse import urlparse
import validators

from scraper.groww_scraper import GrowwScraper


class GrowwScraperPlaywright(GrowwScraper):
    """Playwright-based scraper for JavaScript-rendered Groww pages"""
    
    def __init__(self, headless: bool = True):
        super().__init__()
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
    
    def _setup_browser(self):
        """Setup Playwright browser"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = context.new_page()
        self.page.set_default_timeout(30000)  # 30 seconds
    
    def fetch_page(self, url: str, save_html: bool = False) -> Optional[BeautifulSoup]:
        """Fetch and parse the webpage using Playwright"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        try:
            if self.page is None:
                self._setup_browser()
            
            print(f"Loading page: {url}")
            self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait a bit more for dynamic content to load
            time.sleep(3)
            
            # Scroll to load lazy content
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            self.page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)
            
            # Get page source after JavaScript execution
            page_source = self.page.content()
            
            # Save HTML for debugging if requested
            if save_html:
                import os
                os.makedirs('data/raw_html', exist_ok=True)
                filename = url.split('/')[-1] + '_playwright.html'
                with open(f'data/raw_html/{filename}', 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(page_source)
                print(f"Saved HTML to data/raw_html/{filename}")
            
            return BeautifulSoup(page_source, 'lxml')
            
        except PlaywrightTimeout:
            raise Exception("Timeout waiting for page to load")
        except Exception as e:
            raise Exception(f"Failed to fetch page with Playwright: {str(e)}")
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is a valid Groww URL"""
        if not validators.url(url):
            return False
        
        parsed = urlparse(url)
        if parsed.netloc not in ['groww.in', 'www.groww.in']:
            return False
        
        # Allow both mutual fund URLs and help URLs
        if '/mutual-funds/' not in parsed.path and '/help/' not in parsed.path:
            return False
        
        return True
    
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
                '[class*="schemeName"]',
                '[class*="SchemeName"]',
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5:
                        # Check if it contains UTI or looks like a fund name
                        if 'UTI' in text.upper() or 'Fund' in text or 'Direct' in text:
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
                # Clean up title
                title_text = title_text.replace(' - Groww', '').replace(' | Groww', '').strip()
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
            
            # Look for NAV patterns - more comprehensive, including FAQ format
            nav_patterns = [
                r'NAV[^₹]*₹\s*([\d,]+\.?\d*)\s*as of\s*([^.\n]+)',
                r'NAV[:\s]*₹\s*([\d,]+\.?\d*)\s*\(as of\s*([^)]+)\)',
                r'₹\s*([\d,]+\.?\d*)\s*as of\s*([^.\n]+)',
                r'₹\s*([\d,]+\.?\d*)\s*\(as of\s*([^)]+)\)',
                r'NAV[:\s]*₹\s*([\d,]+\.?\d*)',
                r'Net Asset Value[:\s]*₹\s*([\d,]+\.?\d*)',
            ]
            
            for pattern in nav_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nav_value = match.group(1).replace(',', '')
                    date = match.group(2) if len(match.groups()) > 1 else None
                    if date:
                        date = date.strip()
                    return {
                        'value': nav_value,
                        'date': date
                    }
            
            return None
        except Exception as e:
            print(f"Error extracting NAV: {e}")
            return None
    
    def extract_min_sip(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract minimum SIP amount with enhanced parsing"""
        try:
            text = soup.get_text()
            patterns = [
                r'Min\.?\s*SIP[:\s]*₹\s*([\d,]+)',
                r'Minimum\s+SIP[:\s]*₹\s*([\d,]+)',
                r'SIP[:\s]*₹\s*([\d,]+)',
                r'Min\.?\s*Investment[:\s]*₹\s*([\d,]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1).replace(',', '')
            
            return None
        except Exception as e:
            print(f"Error extracting min SIP: {e}")
            return None
    
    def extract_fund_size(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund size with enhanced parsing"""
        try:
            text = soup.get_text()
            patterns = [
                r'Fund\s+size[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore|Billion)',
                r'Assets\s+Under\s+Management[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore|Billion)',
                r'AUM[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore|Billion)',
                r'Total\s+AUM[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore|Billion)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).replace(',', '')
                    unit = match.group(2) if len(match.groups()) > 1 else 'Cr'
                    return f"{value} {unit}"
            
            return None
        except Exception as e:
            print(f"Error extracting fund size: {e}")
            return None
    
    def _get_html(self, soup: BeautifulSoup) -> str:
        """Return raw HTML text for regex-based parsing"""
        try:
            return soup.decode()
        except Exception:
            return str(soup)
    
    def _extract_analysis_value(self, soup: BeautifulSoup, subject: str) -> Optional[str]:
        """Extract value from analysis_subject JSON blobs present in HTML"""
        html = self._get_html(soup)
        pattern = rf'"analysis_subject":"{subject}".*?"analysis_data":"(.*?)"'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_json_value(self, soup: BeautifulSoup, field: str) -> Optional[str]:
        """Extract simple JSON key value pairs embedded in HTML"""
        html = self._get_html(soup)
        pattern = rf'"{field}":"(.*?)"'
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            try:
                value = bytes(value, 'utf-8').decode('unicode_escape')
            except Exception:
                pass
            return value
        return None
    
    def extract_fund_returns(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract fund returns with enhanced parsing"""
        try:
            text = soup.get_text()
            returns = {}
            
            # Look for returns in various formats
            # Pattern 1: "1Y = 9.3%" or "1Y: 9.3%"
            patterns = [
                r'(\d+Y)\s*[=:]\s*([\d.]+)%',
                r'(\d+)\s*Year[:\s]*([\d.]+)%',
                r'(\d+Y)\s+Return[:\s]*([\d.]+)%',
                r'(\d+Y)\s+([\d.]+)%',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        period = match[0] if 'Y' in match[0].upper() else f"{match[0]}Y"
                        value = match[1]
                        # Only add if it's a reasonable return percentage (0-1000%)
                        try:
                            float_val = float(value)
                            if 0 <= float_val <= 1000:
                                returns[period] = f"{value}%"
                        except:
                            pass
            
            # Remove duplicates - keep first occurrence
            if returns:
                # Filter to only 1Y, 3Y, 5Y if available
                filtered_returns = {}
                for period in ['1Y', '3Y', '5Y']:
                    if period in returns:
                        filtered_returns[period] = returns[period]
                return filtered_returns if filtered_returns else returns
            
            return None
        except Exception as e:
            print(f"Error extracting fund returns: {e}")
            return None
    
    def extract_category_averages(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract category averages with enhanced parsing"""
        try:
            text = soup.get_text()
            averages = {}
            
            # Pattern for "Category averages: 1Y = 4.9%"
            patterns = [
                r'Category\s+averages?[:\s]*(\d+Y)\s*[=:]\s*([\d.]+)%',
                r'Category\s+average[:\s]*(\d+Y)[:\s]*([\d.]+)%',
                r'Category\s+Return[:\s]*(\d+Y)[:\s]*([\d.]+)%',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for period, value in matches:
                    averages[period] = f"{value}%"
            
            return averages if averages else None
        except Exception as e:
            print(f"Error extracting category averages: {e}")
            return None
    
    def extract_rank(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract rank in category with enhanced parsing"""
        try:
            text = soup.get_text()
            ranks = {}
            
            # Pattern for "Rank in category: 1Y=20, 3Y=4, 5Y=5"
            patterns = [
                r'Rank\s+in\s+category[:\s]*(\d+Y)\s*[=:]\s*(\d+)',
                r'Rank[:\s]*(\d+Y)\s*[=:]\s*(\d+)',
                r'(\d+Y)\s*[=:]\s*(\d+)\s*\(rank\)',
                r'Category\s+Rank[:\s]*(\d+Y)[:\s]*(\d+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        period = match[0]
                        rank = match[1]
                        ranks[period] = rank
            
            return ranks if ranks else None
        except Exception as e:
            print(f"Error extracting rank: {e}")
            return None
    
    def extract_expense_ratio(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract expense ratio with enhanced parsing"""
        try:
            text = soup.get_text()
            patterns = [
                r'Expense\s+ratio[^:]*[:\s]*([\d.]+)%',
                r'Total\s+expense\s+ratio[^:]*[:\s]*([\d.]+)%',
                r'TER[:\s]*([\d.]+)%',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return f"{match.group(1)}%"
            
            return None
        except Exception as e:
            print(f"Error extracting expense ratio: {e}")
            return None
    
    def extract_exit_load(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract exit load with enhanced parsing"""
        try:
            # Prefer analysis JSON data if available
            analysis_value = self._extract_analysis_value(soup, 'exit_load')
            if analysis_value:
                value = analysis_value.strip()
                if value.lower() in ['nil', 'zero', 'na', 'n/a']:
                    return 'Nil'
                if value and value.replace('.', '', 1).isdigit() and not value.endswith('%'):
                    return f"{value}%"
                return value
            
            text = soup.get_text()
            patterns = [
                r'Exit\s+load[:\s]*(\d+%)\s*if\s+redeemed\s+within\s+(\d+)\s+year',
                r'Exit\s+load[:\s]*(\d+%)\s*for\s+redemption\s+within\s+(\d+)\s+year',
                r'(\d+%)\s*exit\s+load\s+if\s+redeemed\s+within\s+(\d+)\s+year',
                r'Exit\s+load[:\s]*(\d+%)[^.]*',
                r'(\d+%)\s*exit\s+load',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if len(match.groups()) >= 2:
                        # Format: "1% if redeemed within 1 year"
                        return f"{match.group(1)} if redeemed within {match.group(2)} year"
                    elif len(match.groups()) == 1:
                        value = match.group(1).strip()
                        # Avoid descriptions - only return if it's a percentage
                        if '%' in value and len(value) < 50:
                            return value
            
            return None
        except Exception as e:
            print(f"Error extracting exit load: {e}")
            return None
    
    def extract_stamp_duty(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract stamp duty with enhanced parsing"""
        try:
            text = soup.get_text()
            patterns = [
                r'Stamp\s+duty[:\s]*([\d.]+%)\s*\(policy',
                r'Stamp\s+duty[:\s]*([\d.]+%)',
                r'Stamp\s+duty[:\s]*([\d.]+)\s*%',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result = match.group(1)
                    return result if '%' in result else f"{result}%"
            
            return None
        except Exception as e:
            print(f"Error extracting stamp duty: {e}")
            return None
    
    def extract_lock_in(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract lock-in period information"""
        try:
            analysis_value = self._extract_analysis_value(soup, 'lock_in')
            if analysis_value:
                value = analysis_value.strip().upper()
                if value.endswith('Y'):
                    return value
                if value.isdigit():
                    return f"{value}Y"
                return value
            
            text = soup.get_text()
            match = re.search(r'Lock-?in\s+period[:\s]*([^\n]+)', text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            return None
        except Exception as e:
            print(f"Error extracting lock-in: {e}")
            return None
    
    def extract_scheme_tags(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """Extract scheme type/category tags (e.g., ELSS)"""
        scheme_type = self._extract_json_value(soup, 'scheme_type')
        sub_category = self._extract_json_value(soup, 'sub_category')
        
        result = {
            'scheme_type': scheme_type,
            'sub_category': sub_category,
            'is_elss': 'Yes' if ((sub_category and sub_category.upper() == 'ELSS') or (scheme_type and scheme_type.upper() == 'ELSS')) else 'No',
            'category_label': None
        }
        
        labels = []
        for value in [scheme_type, sub_category]:
            if value and value not in labels:
                labels.append(value)
        if labels:
            result['category_label'] = " ".join(labels)
        
        return result
    
    def extract_fund_manager(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund manager name with enhanced parsing"""
        try:
            # Try to capture sentences mentioning "current fund manager"
            text = self._get_html(soup)
            sentence_match = re.search(
                r'([\w\s,]+?)\s+is\s+the\s+current\s+fund\s+manager',
                text,
                re.IGNORECASE
            )
            if sentence_match:
                possible = sentence_match.group(1)
                # Clean HTML artifacts
                possible = re.sub(r'<[^>]+>', '', possible)
                possible = possible.replace('\\n', ' ').strip()
                possible = re.sub(r'\s+', ' ', possible)
                # Remove generic prefixes
                possible = possible.replace('UTI Mutual Fund', '').strip()
                if possible:
                    return possible
            
            text = soup.get_text()
            patterns = [
                r'Fund\s+Manager[:\s]*([A-Z][a-z]+\s+[A-Z][a-z]+)',  # Full name format
                r'Fund\s+Manager[:\s]*([A-Z]\s+[A-Z][a-z]+)',  # For "V Srivatsa" format
                r'Fund\s+Management[:\s]*([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Managed\s+by[:\s]*([A-Z][a-z]+\s+[A-Z][a-z]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Clean up the name
                    name = re.sub(r'\s+', ' ', name)
                    # Filter out common false positives
                    if name.lower() not in ['s nfo', 'nfo', 'new fund', 'fund offer']:
                        return name
            
            return None
        except Exception as e:
            print(f"Error extracting fund manager: {e}")
            return None
    
    def extract_riskometer(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract riskometer/risk level information"""
        try:
            # Look for riskometer in JSON data first
            risk_level = self._extract_json_value(soup, 'risk_level')
            if risk_level:
                return risk_level.strip()
            
            # Look for risk in JSON data
            risk = self._extract_json_value(soup, 'risk')
            if risk:
                return risk.strip()
            
            # Look for riskometer in text content
            text = soup.get_text()
            
            # Patterns for risk level extraction
            patterns = [
                r'Risk\s+Level[:\s]*([^\n.]+)',
                r'Risk\s+ometer[:\s]*([^\n.]+)',
                r'Risk[:\s]*([^\n.]+?(?:Low|Moderate|High|Very High|Conservative|Aggressive)[^\n.]*?)',
                r'Risk\s+Profile[:\s]*([^\n.]+)',
                r'([^\n.]*?(?:Low|Moderate|High|Very High|Conservative|Aggressive)\s+Risk[^\n.]*)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    risk_text = match.group(1).strip()
                    # Clean up the risk text
                    risk_text = re.sub(r'\s+', ' ', risk_text)
                    if risk_text and len(risk_text) < 100:  # Reasonable length
                        return risk_text
            
            return None
        except Exception as e:
            print(f"Error extracting riskometer: {e}")
            return None
    
    def extract_benchmark(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract benchmark index information"""
        try:
            # Look for benchmark in JSON data first
            benchmark = self._extract_json_value(soup, 'benchmark')
            if benchmark:
                return benchmark.strip()
            
            # Look for benchmark in text content
            text = soup.get_text()
            
            # Patterns for benchmark extraction
            patterns = [
                r'Benchmark[:\s]*([^\n.]+)',
                r'Benchmark\s+Index[:\s]*([^\n.]+)',
                r'Tracks\s+the\s+performance\s+of\s+([^\n.]+?)\s+index',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    benchmark_text = match.group(1).strip()
                    # Clean up the benchmark text
                    benchmark_text = re.sub(r'\s+', ' ', benchmark_text)
                    if benchmark_text and len(benchmark_text) < 150:  # Reasonable length
                        return benchmark_text
            
            return None
        except Exception as e:
            print(f"Error extracting benchmark: {e}")
            return None
    
    def extract_statement_download_info(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract statement download process/instructions"""
        try:
            # Look for information about downloading statements
            text = soup.get_text()
            
            # Patterns for statement download information
            patterns = [
                r'(Download\s+.*?Statement.*?[,.\n])',
                r'(How\s+to\s+download.*?statement[,.\n])',
                r'(Access\s+your\s+.*?statement.*?[,.\n])',
                r'(View\s+.*?Statement.*?[,.\n])',
                r'(Account\s+Statement.*?[,.\n])',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    statement_info = match.group(1).strip()
                    # Clean up the statement info
                    statement_info = re.sub(r'\s+', ' ', statement_info)
                    if statement_info and len(statement_info) < 300:  # Reasonable length
                        return statement_info
            
            # If specific patterns don't work, look for general instructions
            instruction_patterns = [
                r'(You\s+can\s+.*?download.*?from.*?[,.\n])',
                r'(To\s+access.*?[,.\n])',
                r'(Steps\s+to\s+.*?[,.\n])',
                r'(Navigate\s+to.*?[,.\n])',
            ]
            
            for pattern in instruction_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    statement_info = match.group(1).strip()
                    # Clean up the statement info
                    statement_info = re.sub(r'\s+', ' ', statement_info)
                    if statement_info and len(statement_info) < 300:  # Reasonable length
                        return statement_info
            
            return None
        except Exception as e:
            print(f"Error extracting statement download info: {e}")
            return None
    
    def scrape_scheme(self, url: str, save_html: bool = False) -> Dict:
        """Scrape all data from a scheme page"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        soup = self.fetch_page(url, save_html=save_html)
        
        # Debug: Print page title to verify we got the page
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text()}")
        
        # Try to extract JSON data first
        json_data = self.extract_json_data(soup)
        if json_data:
            print("Found JSON data in page, attempting to extract from it...")
            # We can enhance this later to parse JSON data
        
        # Debug: Check if page has JavaScript-rendered content
        script_tags = soup.find_all('script')
        if len(script_tags) > 10:
            print(f"Warning: Page has {len(script_tags)} script tags - may require JavaScript rendering")
        
        scheme_tags = self.extract_scheme_tags(soup)
        
        data = {
            'fund_name': self.extract_fund_name(soup),
            'nav': self.extract_nav(soup),
            'min_sip': self.extract_min_sip(soup),
            'fund_size': self.extract_fund_size(soup),
            'pe_ratio': self.extract_pe_ratio(soup),
            'pb_ratio': self.extract_pb_ratio(soup),
            'fund_returns': self.extract_fund_returns(soup),
            'category_averages': self.extract_category_averages(soup),
            'rank': self.extract_rank(soup),
            'expense_ratio': self.extract_expense_ratio(soup),
            'exit_load': self.extract_exit_load(soup),
            'stamp_duty': self.extract_stamp_duty(soup),
            'fund_manager': self.extract_fund_manager(soup),
            'lock_in': self.extract_lock_in(soup),
            'scheme_type': scheme_tags.get('scheme_type'),
            'sub_category': scheme_tags.get('sub_category'),
            'is_elss': scheme_tags.get('is_elss'),
            'category_label': scheme_tags.get('category_label'),
            'annualised_returns': self.extract_annualised_returns(soup),
            'holdings': self.extract_holdings(soup),
            'risk_metrics': self.extract_risk_metrics(soup),
            'riskometer': self.extract_riskometer(soup),
            'benchmark': self.extract_benchmark(soup),
            'statement_download_info': self.extract_statement_download_info(soup),
            'source_url': url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return data

    def close(self):
        """Close the browser"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.page = None
        self.browser = None
        self.playwright = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

