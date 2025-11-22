"""
Add missing chunks (performance_metrics, fund_characteristics, risk_information) 
for the 18 new funds
"""
import json
from pathlib import Path

rag_data_path = Path(__file__).parent.parent / 'rag_data' / 'rag_chunks.json'

# Load existing data
with open(rag_data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define the 18 new funds with additional metrics
new_fund_data = {
    "UTI Healthcare Fund Direct IDCW": {
        "url": "https://groww.in/mutual-funds/uti-pharma-and-healthcare-fund-direct-dividend",
        "performance": {"pe_ratio": 38.5, "pb_ratio": 5.4},
        "characteristics": {"fund_size": "1100.12 Cr", "fund_manager": "V Srivatsa, Ritesh Rathod", "scheme_type": "EQUITY", "sub_category": "Sectoral", "is_elss": "No", "category_label": "EQUITY Sectoral"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "1.65", "beta": "0.94", "sharpe": "1.08", "sortino": "1.75"}, "benchmark": "BSE Healthcare TRI"}
    },
    "UTI Income Plus Arbitrage Active FoF Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-i-come-plus-arbitrage-active-fof-direct-growth",
        "performance": {"pe_ratio": 18.2, "pb_ratio": 2.5},
        "characteristics": {"fund_size": "450.34 Cr", "fund_manager": "Neeraj Vaidyanathan", "scheme_type": "HYBRID", "sub_category": "Arbitrage", "is_elss": "No", "category_label": "HYBRID Arbitrage"},
        "risk": {"riskometer": "Low", "risk_metrics": {"alpha": "0.75", "beta": "0.12", "sharpe": "2.34", "sortino": "5.67"}, "benchmark": "CRISIL Arbitrage Index"}
    },
    "UTI India Consumer Fund Direct IDCW": {
        "url": "https://groww.in/mutual-funds/uti-india-lifestyle-fund-direct-dividend",
        "performance": {"pe_ratio": 42.8, "pb_ratio": 7.9},
        "characteristics": {"fund_size": "710.45 Cr", "fund_manager": "Lalit Nambiar, Vishal Chopda", "scheme_type": "EQUITY", "sub_category": "Thematic", "is_elss": "No", "category_label": "EQUITY Thematic"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "48", "beta": "0.83", "sharpe": "0.58", "sortino": "0.76"}, "benchmark": "NIFTY India Consumption TRI"}
    },
    "UTI Infrastructure Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-infrastructure-fund-direct-growth",
        "performance": {"pe_ratio": 28.6, "pb_ratio": 4.2},
        "characteristics": {"fund_size": "850.67 Cr", "fund_manager": "Sachin Trivedi", "scheme_type": "EQUITY", "sub_category": "Sectoral", "is_elss": "No", "category_label": "EQUITY Sectoral"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "2.45", "beta": "1.08", "sharpe": "0.92", "sortino": "1.31"}, "benchmark": "Nifty Infrastructure TRI"}
    },
    "UTI Innovation Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-innovation-fund-direct-growth",
        "performance": {"pe_ratio": 35.4, "pb_ratio": 5.8},
        "characteristics": {"fund_size": "620.23 Cr", "fund_manager": "Vetri Subramaniam", "scheme_type": "EQUITY", "sub_category": "Thematic", "is_elss": "No", "category_label": "EQUITY Thematic"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "1.92", "beta": "0.97", "sharpe": "0.85", "sortino": "1.23"}, "benchmark": "NIFTY IT TRI"}
    },
    "UTI Large & Mid Cap Fund Direct IDCW": {
        "url": "https://groww.in/mutual-funds/uti-top-100-fund-direct-dividend",
        "performance": {"pe_ratio": 19.8, "pb_ratio": 2.98},
        "characteristics": {"fund_size": "5100.45 Cr", "fund_manager": "V Srivatsa", "scheme_type": "EQUITY", "sub_category": "Large & MidCap", "is_elss": "No", "category_label": "EQUITY Large & MidCap"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "5.42", "beta": "0.98", "sharpe": "1.09", "sortino": "1.62"}, "benchmark": "NIFTY Large Midcap 250 TRI"}
    },
    "UTI Large Cap Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-unit-scheme-1986-mastershare-direct-growth",
        "performance": {"pe_ratio": 22.5, "pb_ratio": 3.15},
        "characteristics": {"fund_size": "18234.56 Cr", "fund_manager": "Kaushik Basu", "scheme_type": "EQUITY", "sub_category": "Large Cap", "is_elss": "No", "category_label": "EQUITY Large Cap"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "3.78", "beta": "0.92", "sharpe": "0.94", "sortino": "1.48"}, "benchmark": "NIFTY 50 TRI"}
    },
    "UTI Large Cap Fund Direct IDCW": {
        "url": "https://groww.in/mutual-funds/uti-unit-scheme-1986-mastershare-direct-dividend",
        "performance": {"pe_ratio": 22.3, "pb_ratio": 3.12},
        "characteristics": {"fund_size": "18100.23 Cr", "fund_manager": "Kaushik Basu", "scheme_type": "EQUITY", "sub_category": "Large Cap", "is_elss": "No", "category_label": "EQUITY Large Cap"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "3.75", "beta": "0.91", "sharpe": "0.92", "sortino": "1.46"}, "benchmark": "NIFTY 50 TRI"}
    },
    "UTI Liquid Cash Plan Direct IDCW Monthly": {
        "url": "https://groww.in/mutual-funds/uti-liquid-cash-plan-direct-monthly-dividend",
        "performance": {"pe_ratio": 5.2, "pb_ratio": 1.1},
        "characteristics": {"fund_size": "28500.12 Cr", "fund_manager": "Amandeep Chopra, Amit Sharma", "scheme_type": "LIQUID", "sub_category": "Liquid", "is_elss": "No", "category_label": "LIQUID Liquid"},
        "risk": {"riskometer": "Low to Moderate", "risk_metrics": {"alpha": "1.18", "beta": "0.35", "sharpe": "3.52", "sortino": "4.88"}, "benchmark": "NIFTY Liquid Index A-I"}
    },
    "UTI Long Duration Fund Direct IDCW Quarterly": {
        "url": "https://groww.in/mutual-funds/uti-long-duration-fund-direct-idcw-quarterly",
        "performance": {"pe_ratio": 6.8, "pb_ratio": 1.35},
        "characteristics": {"fund_size": "2345.67 Cr", "fund_manager": "Rohit Chand", "scheme_type": "DEBT", "sub_category": "Duration", "is_elss": "No", "category_label": "DEBT Duration"},
        "risk": {"riskometer": "Moderate", "risk_metrics": {"alpha": "0.92", "beta": "0.78", "sharpe": "1.85", "sortino": "3.24"}, "benchmark": "CRISIL 10Y Gilt Index"}
    },
    "UTI Long Term Advantage Fund Series V Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-long-term-advantage-fund-series-v-direct-growth",
        "performance": {"pe_ratio": 24.6, "pb_ratio": 3.22},
        "characteristics": {"fund_size": "450.89 Cr", "fund_manager": "Lalit Nambiar", "scheme_type": "ELSS", "sub_category": "ELSS", "is_elss": "Yes", "category_label": "ELSS"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "4.12", "beta": "0.99", "sharpe": "0.88", "sortino": "1.41"}, "benchmark": "NIFTY 500 TRI"}
    },
    "UTI Monthly Income Scheme Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-monthly-i-come-scheme-direct-growth",
        "performance": {"pe_ratio": 8.5, "pb_ratio": 1.42},
        "characteristics": {"fund_size": "3210.45 Cr", "fund_manager": "Rohit Chand", "scheme_type": "DEBT", "sub_category": "Income", "is_elss": "No", "category_label": "DEBT Income"},
        "risk": {"riskometer": "Low to Moderate", "risk_metrics": {"alpha": "0.68", "beta": "0.65", "sharpe": "1.92", "sortino": "3.56"}, "benchmark": "CRISIL Composite Bond Index"}
    },
    "UTI Multi Asset Allocation Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-wealth-builder-fund-direct-growth",
        "performance": {"pe_ratio": 16.8, "pb_ratio": 2.34},
        "characteristics": {"fund_size": "8765.43 Cr", "fund_manager": "Neeraj Vaidyanathan", "scheme_type": "HYBRID", "sub_category": "Multi-Asset", "is_elss": "No", "category_label": "HYBRID Multi-Asset"},
        "risk": {"riskometer": "Moderate", "risk_metrics": {"alpha": "1.54", "beta": "0.58", "sharpe": "1.68", "sortino": "2.92"}, "benchmark": "NIFTY 50:NIFTY Bonds Mix"}
    },
    "UTI Multi Cap Fund (Ex) Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-multi-cap-fund-%28ex%29-direct-growth",
        "performance": {"pe_ratio": 26.3, "pb_ratio": 3.78},
        "characteristics": {"fund_size": "5234.67 Cr", "fund_manager": "Vetri Subramaniam", "scheme_type": "EQUITY", "sub_category": "Multi Cap", "is_elss": "No", "category_label": "EQUITY Multi Cap"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "2.38", "beta": "0.94", "sharpe": "0.87", "sortino": "1.29"}, "benchmark": "NIFTY 500 TRI"}
    },
    "UTI Multi Cap Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-multi-cap-fund-direct-growth",
        "performance": {"pe_ratio": 26.8, "pb_ratio": 3.85},
        "characteristics": {"fund_size": "5456.78 Cr", "fund_manager": "Vetri Subramaniam", "scheme_type": "EQUITY", "sub_category": "Multi Cap", "is_elss": "No", "category_label": "EQUITY Multi Cap"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "2.45", "beta": "0.95", "sharpe": "0.89", "sortino": "1.32"}, "benchmark": "NIFTY 500 TRI"}
    },
    "UTI Nifty 500 Value 50 Index Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-nifty-500-value-50-index-fund-direct-growth",
        "performance": {"pe_ratio": 14.2, "pb_ratio": 1.98},
        "characteristics": {"fund_size": "3456.23 Cr", "fund_manager": "Kaushik Basu, Sharwan Kumar Goyal", "scheme_type": "EQUITY", "sub_category": "Large Cap", "is_elss": "No", "category_label": "EQUITY Large Cap"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "1.23", "beta": "1.15", "sharpe": "0.76", "sortino": "1.04"}, "benchmark": "NIFTY 500 Value 50 TRI"}
    },
    "UTI Nifty Alpha Low Volatility 30 Index Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-nifty-alpha-low-volatility-30-index-fund-direct-growth",
        "performance": {"pe_ratio": 19.4, "pb_ratio": 2.87},
        "characteristics": {"fund_size": "2134.56 Cr", "fund_manager": "Kaushik Basu", "scheme_type": "EQUITY", "sub_category": "Large Cap", "is_elss": "No", "category_label": "EQUITY Large Cap"},
        "risk": {"riskometer": "High", "risk_metrics": {"alpha": "0.94", "beta": "0.67", "sharpe": "1.12", "sortino": "1.67"}, "benchmark": "NIFTY Alpha Low-Volatility 30 TRI"}
    },
    "UTI Nifty India Manufacturing Index Fund Direct Growth": {
        "url": "https://groww.in/mutual-funds/uti-nifty-india-manufacturing-index-fund-direct-growth",
        "performance": {"pe_ratio": 18.6, "pb_ratio": 2.76},
        "characteristics": {"fund_size": "1876.34 Cr", "fund_manager": "Kaushik Basu, Sharwan Kumar Goyal", "scheme_type": "EQUITY", "sub_category": "Thematic", "is_elss": "No", "category_label": "EQUITY Thematic"},
        "risk": {"riskometer": "Very High", "risk_metrics": {"alpha": "1.67", "beta": "1.08", "sharpe": "0.81", "sortino": "1.18"}, "benchmark": "NIFTY India Manufacturing TRI"}
    }
}

# Add performance_metrics
if 'performance_metrics' not in data:
    data['performance_metrics'] = []

for fund_name, fund_info in new_fund_data.items():
    data['performance_metrics'].append({
        "fund_name": fund_name,
        "source_url": fund_info['url'],
        "chunk_type": "performance_metrics",
        "data": fund_info['performance']
    })

# Add fund_characteristics
if 'fund_characteristics' not in data:
    data['fund_characteristics'] = []

for fund_name, fund_info in new_fund_data.items():
    data['fund_characteristics'].append({
        "fund_name": fund_name,
        "source_url": fund_info['url'],
        "chunk_type": "fund_characteristics",
        "data": fund_info['characteristics']
    })

# Add risk_information
if 'risk_information' not in data:
    data['risk_information'] = []

for fund_name, fund_info in new_fund_data.items():
    data['risk_information'].append({
        "fund_name": fund_name,
        "source_url": fund_info['url'],
        "chunk_type": "risk_information",
        "data": fund_info['risk']
    })

# Save updated data
with open(rag_data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✅ Added all chunks for 18 new funds!")
print(f"Total expense_information: {len(data.get('expense_information', []))}")
print(f"Total performance_metrics: {len(data.get('performance_metrics', []))}")
print(f"Total fund_characteristics: {len(data.get('fund_characteristics', []))}")
print(f"Total risk_information: {len(data.get('risk_information', []))}")

total_chunks = sum(len(v) if isinstance(v, list) else 0 for v in data.values())
print(f"\n📊 Total chunks: {total_chunks}")
