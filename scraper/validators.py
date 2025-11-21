"""
Data validation utilities for scraped mutual fund data
"""

import re
from typing import Dict, Optional, List
from datetime import datetime


class DataValidator:
    """Validates scraped mutual fund data"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url or not isinstance(url, str):
            return False
        
        url_pattern = re.compile(
            r'^https?://(www\.)?groww\.in/mutual-funds/[\w-]+$'
        )
        return bool(url_pattern.match(url))
    
    @staticmethod
    def validate_fund_name(name: Optional[str]) -> bool:
        """Validate fund name"""
        if not name:
            return False
        if len(name) < 5 or len(name) > 200:
            return False
        return True
    
    @staticmethod
    def validate_nav(nav: Optional[Dict]) -> bool:
        """Validate NAV data"""
        if not nav:
            return False
        if 'value' not in nav:
            return False
        try:
            float(nav['value'].replace(',', ''))
            return True
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def validate_amount(amount: Optional[str]) -> bool:
        """Validate amount (SIP, fund size, etc.)"""
        if not amount:
            return False
        # Remove currency symbols, commas, and common units (Cr, Lakh, etc.)
        clean_amount = re.sub(r'[₹,\s]', '', str(amount))
        clean_amount = re.sub(r'(Cr|Lakh|Crore|Billion|Million)', '', clean_amount, flags=re.IGNORECASE)
        try:
            float(clean_amount)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_percentage(value: Optional[str]) -> bool:
        """Validate percentage value"""
        if not value:
            return False
        # Remove % sign
        clean_value = re.sub(r'[%\s]', '', str(value))
        try:
            float_val = float(clean_value)
            # Reasonable range for percentages
            return -100 <= float_val <= 1000
        except ValueError:
            return False
    
    @staticmethod
    def validate_ratio(value: Optional[str]) -> bool:
        """Validate ratio (P/E, P/B)"""
        if not value:
            return False
        try:
            float_val = float(str(value))
            # Reasonable range for ratios
            return 0 <= float_val <= 1000
        except ValueError:
            return False
    
    @staticmethod
    def validate_returns(returns: Optional[Dict]) -> bool:
        """Validate returns data"""
        if not returns:
            return False
        if not isinstance(returns, dict):
            return False
        # At least one return period should be present
        return len(returns) > 0
    
    @staticmethod
    def validate_rank(rank: Optional[Dict]) -> bool:
        """Validate rank data"""
        if not rank:
            return False
        if not isinstance(rank, dict):
            return False
        # Rank should be positive integers
        for period, rank_value in rank.items():
            try:
                rank_int = int(str(rank_value))
                if rank_int < 1:
                    return False
            except ValueError:
                return False
        return True
    
    @staticmethod
    def validate_fund_manager(manager: Optional[str]) -> bool:
        """Validate fund manager name"""
        if not manager:
            return False
        if len(manager) < 2 or len(manager) > 100:
            return False
        # Should contain at least one letter
        if not re.search(r'[A-Za-z]', manager):
            return False
        return True
    
    @staticmethod
    def validate_risk_metrics(metrics: Optional[Dict]) -> bool:
        """Validate risk metrics"""
        if not metrics:
            return False
        if not isinstance(metrics, dict):
            return False
        # Each metric should be a valid float
        for metric, value in metrics.items():
            try:
                float(str(value))
            except ValueError:
                return False
        return True
    
    @staticmethod
    def validate_riskometer(riskometer: Optional[str]) -> bool:
        """Validate riskometer information"""
        if not riskometer:
            return False
        if not isinstance(riskometer, str):
            return False
        # Should be a reasonable length
        if len(riskometer) < 2 or len(riskometer) > 100:
            return False
        return True
    
    @staticmethod
    def validate_benchmark(benchmark: Optional[str]) -> bool:
        """Validate benchmark information"""
        if not benchmark:
            return False
        if not isinstance(benchmark, str):
            return False
        # Should be a reasonable length
        if len(benchmark) < 5 or len(benchmark) > 150:
            return False
        return True
    
    @staticmethod
    def validate_statement_download_info(statement_info: Optional[str]) -> bool:
        """Validate statement download information"""
        if not statement_info:
            return False
        if not isinstance(statement_info, str):
            return False
        # Should be a reasonable length
        if len(statement_info) < 10 or len(statement_info) > 500:
            return False
        return True
    
    @staticmethod
    def validate_scraped_data(data: Dict) -> Dict[str, List[str]]:
        """
        Validate all scraped data and return validation errors
        Returns: Dict with 'errors' and 'warnings' lists
        """
        errors = []
        warnings = []
        
        # Validate source URL
        if not DataValidator.validate_url(data.get('source_url', '')):
            errors.append("Invalid or missing source URL")
        
        # Validate fund name
        if not DataValidator.validate_fund_name(data.get('fund_name')):
            errors.append("Invalid or missing fund name")
        
        # Validate NAV
        if not DataValidator.validate_nav(data.get('nav')):
            warnings.append("NAV data missing or invalid")
        
        # Validate minimum SIP
        if not DataValidator.validate_amount(data.get('min_sip')):
            warnings.append("Minimum SIP amount missing or invalid")
        
        # Validate fund size
        if not DataValidator.validate_amount(data.get('fund_size')):
            warnings.append("Fund size missing or invalid")
        
        # Validate expense ratio
        if not DataValidator.validate_percentage(data.get('expense_ratio')):
            warnings.append("Expense ratio missing or invalid")
        
        # Validate exit load (can be None, but if present should be valid)
        exit_load = data.get('exit_load')
        if exit_load and not isinstance(exit_load, str):
            warnings.append("Exit load format invalid")
        
        # Validate fund manager
        if not DataValidator.validate_fund_manager(data.get('fund_manager')):
            warnings.append("Fund manager name missing or invalid")
        
        # Validate returns
        if not DataValidator.validate_returns(data.get('fund_returns')):
            warnings.append("Fund returns missing or invalid")
        
        # Validate category averages
        if data.get('category_averages') and not DataValidator.validate_returns(data.get('category_averages')):
            warnings.append("Category averages format invalid")
        
        # Validate rank
        if data.get('rank') and not DataValidator.validate_rank(data.get('rank')):
            warnings.append("Rank data format invalid")
        
        # Validate risk metrics
        if data.get('risk_metrics') and not DataValidator.validate_risk_metrics(data.get('risk_metrics')):
            warnings.append("Risk metrics format invalid")
        
        # Validate riskometer
        if data.get('riskometer') and not DataValidator.validate_riskometer(data.get('riskometer')):
            warnings.append("Riskometer information format invalid")
        
        # Validate benchmark
        if data.get('benchmark') and not DataValidator.validate_benchmark(data.get('benchmark')):
            warnings.append("Benchmark information format invalid")
        
        # Validate statement download info
        if data.get('statement_download_info') and not DataValidator.validate_statement_download_info(data.get('statement_download_info')):
            warnings.append("Statement download information format invalid")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'is_valid': len(errors) == 0
        }

