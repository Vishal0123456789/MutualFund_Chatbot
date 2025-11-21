# UTI Mutual Fund FAQ Assistant - Data Extraction

This project implements a data extraction system for UTI mutual fund schemes from Groww platform. The extracted data will be used to build an FAQ chatbot.

## Project Structure

```
faq-assistant/
├── scraper/
│   ├── __init__.py
│   ├── groww_scraper.py      # Main scraper for Groww pages
│   └── validators.py          # Data validation utilities
├── database/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy database models
│   └── db_manager.py          # Database operations
├── scripts/
│   ├── test_scraper.py        # Test script for single URL
│   └── scrape_uti_schemes.py  # Batch scraping script
├── data/                      # Database and scraped data (created at runtime)
├── requirements.txt
└── README.md
```

## Features

- ✅ Scrapes comprehensive data from Groww mutual fund scheme pages
- ✅ Validates all scraped data
- ✅ Stores data with source URLs in SQLite database
- ✅ Supports batch scraping of multiple schemes
- ✅ Error handling and logging

## Data Points Extracted

For each UTI mutual fund scheme, the scraper extracts:

1. **Fund Name** - Full name of the scheme
2. **NAV** - Net Asset Value with date
3. **Min. SIP Amount** - Minimum SIP investment
4. **Fund Size** - Assets Under Management (AUM)
5. **P/E Ratio** - Price to Earnings ratio
6. **P/B Ratio** - Price to Book ratio
7. **Fund Returns** - 1Y, 3Y, 5Y returns
8. **Category Averages** - Category average returns
9. **Rank** - Rank within category
10. **Expense Ratio** - Total expense ratio
11. **Exit Load** - Exit load details
12. **Stamp Duty** - Stamp duty percentage
13. **Fund Manager** - Fund manager name
14. **Annualised Returns** - 3Y and 5Y annualised returns
15. **Holdings** - Top holdings (if available)
16. **Risk Metrics** - Alpha, Beta, Sharpe, Sortino ratios

## Installation

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Test Single Scheme

Test the scraper with a single URL:

```bash
python scripts/test_scraper.py "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth"
```

### Scrape Multiple Schemes

Scrape multiple UTI schemes:

```bash
python scripts/scrape_uti_schemes.py
```

Or provide URLs as arguments:

```bash
python scripts/scrape_uti_schemes.py "https://groww.in/mutual-funds/uti-healthcare-fund-direct-growth" "https://groww.in/mutual-funds/uti-india-consumer-fund-direct-growth"
```

Or provide a file with URLs (one per line):

```bash
python scripts/scrape_uti_schemes.py urls.txt
```

## Database

The scraped data is stored in SQLite database at `data/mutual_funds.db`.

### Database Schema

- **schemes** - Stores scheme information
- **scheme_data** - Stores individual data points with source URLs
- **scrape_logs** - Logs all scraping activities

## Data Validation

All scraped data is validated using the `DataValidator` class:

- URL validation
- Data type validation
- Range validation
- Format validation

Validation results include:
- **Errors** - Critical issues that prevent data saving
- **Warnings** - Non-critical issues (missing optional data)

## Source URL Tracking

Every data point is stored with its source URL from Groww website. This ensures:
- Traceability of information
- Ability to verify data
- Compliance with data attribution requirements

## Example Output

```json
{
  "fund_name": "UTI Large & Mid Cap Fund Direct Growth",
  "nav": {
    "value": "199.23",
    "date": "14 Nov 2025"
  },
  "min_sip": "500",
  "fund_size": "5291.10 Cr",
  "fund_returns": {
    "1Y": "9.3%",
    "3Y": "22.4%",
    "5Y": "25.2%"
  },
  "category_averages": {
    "1Y": "4.9%",
    "3Y": "17.5%",
    "5Y": "20.6%"
  },
  "rank": {
    "1Y": "20",
    "3Y": "4",
    "5Y": "5"
  },
  "expense_ratio": "0.97%",
  "exit_load": "1% if redeemed within 1 year",
  "stamp_duty": "0.005%",
  "fund_manager": "V Srivatsa",
  "source_url": "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth",
  "scraped_at": "2025-01-XX XX:XX:XX"
}
```

## Notes

- The scraper respects rate limiting with delays between requests
- All URLs are validated before scraping
- Data is validated before saving to database
- Failed scrapes are logged for debugging

## Next Steps

1. ✅ Data extraction (Current)
2. ⏳ Generate embeddings for RAG
3. ⏳ Build chatbot API
4. ⏳ Create frontend interface
5. ⏳ Implement data refresh system

## License

This project is for educational purposes only. Please respect Groww's terms of service and robots.txt when scraping.

