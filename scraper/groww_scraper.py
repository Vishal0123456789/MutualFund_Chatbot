"""
Groww Mutual Fund Scheme Scraper
Scrapes data from Groww mutual fund scheme pages
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Optional, List
from urllib.parse import urlparse
import validators
import time


class GrowwScraper:
    """Scraper for Groww mutual fund scheme pages"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is a valid Groww mutual fund URL"""
        if not validators.url(url):
            return False
        
        parsed = urlparse(url)
        if parsed.netloc not in ['groww.in', 'www.groww.in']:
            return False
        
        # Allow both mutual fund URLs and help URLs
        if '/mutual-funds/' not in parsed.path and '/help/' not in parsed.path:
            return False
        
        return True
    
    def fetch_page(self, url: str, save_html: bool = False) -> Optional[BeautifulSoup]:
        """Fetch and parse the webpage"""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Save HTML for debugging if requested
            if save_html:
                import os
                os.makedirs('data/raw_html', exist_ok=True)
                filename = url.split('/')[-1] + '.html'
                with open(f'data/raw_html/{filename}', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"Saved HTML to data/raw_html/{filename}")
            
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch page: {str(e)}")
    
    def extract_fund_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund name"""
        try:
            # Try multiple selectors
            selectors = [
                'h1',
                '[data-testid="fund-name"]',
                '.fund-name',
                'h1.fund-title',
                'h1[class*="fund"]',
                '[class*="fundName"]',
                '[class*="fund-name"]',
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 5:
                        return text
            
            # Look for meta tags
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                title_text = og_title.get('content')
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
                return title_text.strip()
            
            # Fallback: look for title tag
            title = soup.find('title')
            if title:
                title_text = title.get_text(strip=True)
                # Extract fund name from title
                if '|' in title_text:
                    return title_text.split('|')[0].strip()
                return title_text
            
            return None
        except Exception as e:
            print(f"Error extracting fund name: {e}")
            return None
    
    def extract_nav(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract NAV and date"""
        try:
            # Look for NAV in specific HTML elements first
            nav_selectors = [
                '[class*="nav"]',
                '[class*="NAV"]',
                '[data-testid*="nav"]',
            ]
            
            for selector in nav_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text()
                    # Look for NAV pattern with date
                    match = re.search(r'₹\s*([\d,]+\.?\d*)\s*\(as of\s*([^)]+)\)', text, re.IGNORECASE)
                    if match:
                        return {
                            'value': match.group(1).replace(',', ''),
                            'date': match.group(2).strip()
                        }
                    # Look for NAV without date
                    match = re.search(r'₹\s*([\d,]+\.?\d*)', text)
                    if match:
                        return {
                            'value': match.group(1).replace(',', ''),
                            'date': None
                        }
            
            # Look for NAV patterns in full text
            text = soup.get_text()
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
    
    def extract_min_sip(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract minimum SIP amount"""
        try:
            text = soup.get_text()
            patterns = [
                r'Min\.?\s*SIP[:\s]*₹\s*([\d,]+)',
                r'Minimum\s+SIP[:\s]*₹\s*([\d,]+)',
                r'SIP[:\s]*₹\s*([\d,]+)',
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
        """Extract fund size"""
        try:
            text = soup.get_text()
            patterns = [
                r'Fund\s+size[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore)',
                r'Assets\s+Under\s+Management[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore)',
                r'AUM[:\s]*₹\s*([\d,]+\.?\d*)\s*(Cr|Lakh|Crore)',
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
        """Return raw HTML for regex parsing"""
        try:
            return soup.decode()
        except Exception:
            return str(soup)
    
    def _extract_analysis_value(self, soup: BeautifulSoup, subject: str) -> Optional[str]:
        """Extract value from analysis_subject JSON blobs"""
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
    
    def extract_pe_ratio(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract P/E ratio"""
        try:
            text = soup.get_text()
            patterns = [
                r'P/E\s+ratio[:\s]*([\d.]+)',
                r'Price[-\s]to[-\s]Earnings[:\s]*([\d.]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"Error extracting P/E ratio: {e}")
            return None
    
    def extract_pb_ratio(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract P/B ratio"""
        try:
            text = soup.get_text()
            patterns = [
                r'P/B\s+ratio[:\s]*([\d.]+)',
                r'Price[-\s]to[-\s]Book[:\s]*([\d.]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"Error extracting P/B ratio: {e}")
            return None
    
    def extract_fund_returns(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract fund returns (1Y, 3Y, 5Y)"""
        try:
            text = soup.get_text()
            returns = {}
            
            # Pattern for returns like "1Y = 9.3%" or "Fund returns: 1Y = 9.3%"
            patterns = [
                r'Fund\s+returns[:\s]*(\d+Y)\s*[=:]\s*([\d.]+)%',
                r'(\d+Y)\s*[=:]\s*([\d.]+)%',
                r'(\d+)\s*Year[:\s]*([\d.]+)%',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        period = match[0] if 'Y' in match[0].upper() else f"{match[0]}Y"
                        value = match[1]
                        returns[period] = f"{value}%"
            
            # Remove duplicates and keep the most specific match
            if returns:
                return returns
            
            return None
        except Exception as e:
            print(f"Error extracting fund returns: {e}")
            return None
    
    def extract_category_averages(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract category averages"""
        try:
            text = soup.get_text()
            averages = {}
            
            # Pattern for "Category averages: 1Y = 4.9%"
            patterns = [
                r'Category\s+averages?[:\s]*(\d+Y)\s*[=:]\s*([\d.]+)%',
                r'Category\s+average[:\s]*(\d+Y)[:\s]*([\d.]+)%',
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
        """Extract rank in category"""
        try:
            text = soup.get_text()
            ranks = {}
            
            # Pattern for "Rank in category: 1Y=20, 3Y=4, 5Y=5"
            patterns = [
                r'Rank\s+in\s+category[:\s]*(\d+Y)\s*[=:]\s*(\d+)',
                r'Rank[:\s]*(\d+Y)\s*[=:]\s*(\d+)',
                r'(\d+Y)\s*[=:]\s*(\d+)\s*\(rank\)',
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
        """Extract expense ratio"""
        try:
            text = soup.get_text()
            patterns = [
                r'Expense\s+ratio[^:]*[:\s]*([\d.]+)%',
                r'Total\s+expense\s+ratio[^:]*[:\s]*([\d.]+)%',
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
        """Extract exit load"""
        try:
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
            ]
            
            basic_patterns = [
                r'Exit\s+load[:\s]*(\d+%)[^.]*',
                r'Exit\s+load[:\s]*([^.\n]+?)(?:\.|$)',
                r'(\d+%)\s*exit\s+load',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    if len(match.groups()) > 1:
                        # Format: "1% if redeemed within 1 year"
                        return f"{match.group(1)} if redeemed within {match.group(2)} year"
            
            for pattern in basic_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if '%' in value and len(value) < 50:
                        return value
            
            return None
        except Exception as e:
            print(f"Error extracting exit load: {e}")
            return None
    
    def extract_stamp_duty(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract stamp duty"""
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
        """Extract lock-in period"""
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
        """Extract scheme type/category tags"""
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
        """Extract fund manager name"""
        try:
            text = self._get_html(soup)
            sentence_match = re.search(
                r'([\w\s,]+?)\s+is\s+the\s+current\s+fund\s+manager',
                text,
                re.IGNORECASE
            )
            if sentence_match:
                possible = sentence_match.group(1)
                possible = re.sub(r'<[^>]+>', '', possible)
                possible = possible.replace('\n', ' ').strip()
                possible = re.sub(r'\s+', ' ', possible)
                possible = possible.replace('UTI Mutual Fund', '').strip()
                if possible:
                    return possible
            
            text = soup.get_text()
            patterns = [
                r'Fund\s+Manager[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Fund\s+Management[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'Fund\s+Manager[:\s]*([A-Z]\s+[A-Z][a-z]+)',  # For "V Srivatsa" format
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    # Clean up the name
                    name = re.sub(r'\s+', ' ', name)
                    if name.lower() in ['s nfo', 'nfo', 'new fund', 'fund offer']:
                        continue
                    return name
            
            return None
        except Exception as e:
            print(f"Error extracting fund manager: {e}")
            return None
    
    def extract_annualised_returns(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract 3Y and 5Y annualised returns"""
        try:
            text = soup.get_text()
            returns = {}
            
            pattern = r'(\d+Y)\s+annualised[:\s]*([\d.]+)%'
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for period, value in matches:
                returns[period] = f"{value}%"
            
            return returns if returns else None
        except Exception as e:
            print(f"Error extracting annualised returns: {e}")
            return None
    
    def extract_holdings(self, soup: BeautifulSoup) -> Optional[List[Dict]]:
        """Extract top holdings"""
        try:
            holdings = []
            # Look for holdings table or list
            # This will need to be customized based on actual page structure
            # For now, return None and we'll enhance based on actual page structure
            return None
        except Exception as e:
            print(f"Error extracting holdings: {e}")
            return None
    
    def extract_risk_metrics(self, soup: BeautifulSoup) -> Optional[Dict[str, str]]:
        """Extract Alpha, Beta, Sharpe, Sortino ratios"""
        try:
            text = soup.get_text()
            metrics = {}
            
            patterns = {
                'alpha': r'Alpha[:\s]*([\d.]+)',
                'beta': r'Beta[:\s]*([\d.]+)',
                'sharpe': r'Sharpe[:\s]*([\d.]+)',
                'sortino': r'Sortino[:\s]*([\d.]+)',
            }
            
            for metric, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    metrics[metric] = match.group(1)
            
            return metrics if metrics else None
        except Exception as e:
            print(f"Error extracting risk metrics: {e}")
            return None
    
    def extract_riskometer(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract riskometer/risk level information"""
        try:
            # Look for riskometer in JSON-like data first
            html = self._get_html(soup)
            pattern = r'"risk_level":"(.*?)"'
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            # Look for risk in JSON-like data
            pattern = r'"risk":"(.*?)"'
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
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
            # Look for benchmark in JSON-like data first
            html = self._get_html(soup)
            pattern = r'"benchmark":"(.*?)"'
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
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
    
    def extract_json_data(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract JSON data from script tags (common in React/Next.js apps)"""
        try:
            # Look for JSON in script tags
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        return data
                except:
                    continue
            
            # Look for __NEXT_DATA__ or similar
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('__NEXT_DATA__' in script.string or 'window.__' in script.string):
                    # Try to extract JSON
                    text = script.string
                    # Look for JSON object
                    json_match = re.search(r'\{.*\}', text, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(0))
                            if isinstance(data, dict):
                                return data
                        except:
                            continue
            
            return None
        except Exception as e:
            print(f"Error extracting JSON data: {e}")
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

