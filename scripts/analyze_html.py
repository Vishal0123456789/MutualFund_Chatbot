"""
Script to analyze the saved HTML and improve extraction patterns
"""

import sys
import os
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup


def analyze_html_for_patterns(html_file_path):
    """Analyze HTML file to find better extraction patterns"""
    print(f"Analyzing HTML file: {html_file_path}")
    
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Get text content
    text = soup.get_text()
    
    print("\n=== ANALYSIS RESULTS ===")
    
    # Look for risk-related terms
    print("\n1. Risk-related terms found:")
    risk_patterns = [
        r'Risk\s+Level[:\s]*([^\n.]+)',
        r'Risk\s+ometer[:\s]*([^\n.]+)',
        r'Risk\s+Profile[:\s]*([^\n.]+)',
        r'Risk[:\s]*([^\n.]+?(?:Low|Moderate|High|Very High|Conservative|Aggressive)[^\n.]*?)',
    ]
    
    for pattern in risk_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"   Pattern '{pattern}': {matches}")
    
    # Look for statement-related terms
    print("\n2. Statement-related terms found:")
    statement_patterns = [
        r'(Download\s+.*?Statement)',
        r'(How\s+to\s+download.*?statement)',
        r'(Access\s+your\s+.*?statement)',
        r'(View\s+.*?Statement)',
        r'(Account\s+Statement)',
        r'(Steps\s+to\s+.*?download)',
        r'(Navigate\s+to.*?statement)',
    ]
    
    for pattern in statement_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            print(f"   Pattern '{pattern}': {matches}")
    
    # Look for JSON data that might contain risk information
    print("\n3. JSON data analysis:")
    json_patterns = [
        r'"risk_level":"(.*?)"',
        r'"risk":"(.*?)"',
        r'"riskProfile":"(.*?)"',
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        if matches:
            print(f"   Pattern '{pattern}': {matches}")
    
    # Look for specific elements in HTML
    print("\n4. HTML element analysis:")
    # Look for common risk display elements
    risk_elements = soup.find_all(['div', 'span', 'p'], string=re.compile(r'Risk', re.IGNORECASE))
    if risk_elements:
        print(f"   Risk-related HTML elements: {len(risk_elements)} found")
        for elem in risk_elements[:3]:  # Show first 3
            print(f"     - {elem.name}: {elem.get_text()[:100]}...")
    
    # Look for statement/download elements
    statement_elements = soup.find_all(['div', 'span', 'p', 'a'], string=re.compile(r'(Statement|Download)', re.IGNORECASE))
    if statement_elements:
        print(f"   Statement/Download HTML elements: {len(statement_elements)} found")
        for elem in statement_elements[:3]:  # Show first 3
            print(f"     - {elem.name}: {elem.get_text()[:100]}...")


if __name__ == "__main__":
    # Look for the saved HTML file
    html_dir = Path("c:/Users/satis/Milestone 1/data/raw_html")
    if html_dir.exists():
        html_files = list(html_dir.glob("*playwright.html"))
        if html_files:
            analyze_html_for_patterns(html_files[0])
        else:
            print("No HTML files found in data/raw_html directory")
    else:
        print("data/raw_html directory not found")