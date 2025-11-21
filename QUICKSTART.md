# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **pip** package manager

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using pip3:

```bash
pip3 install -r requirements.txt
```

### 2. Test the Scraper

Test with a single scheme URL:

```bash
python scripts/test_scraper.py "https://groww.in/mutual-funds/uti-large-mid-cap-fund-direct-growth"
```

### 3. Scrape Multiple Schemes

Edit `scripts/scrape_uti_schemes.py` to add more URLs, then run:

```bash
python scripts/scrape_uti_schemes.py
```

## Expected Output

When you run the test script, you should see:

1. ✅ URL validation
2. 📥 Page fetching
3. 📊 Scraped data (JSON format)
4. 🔍 Validation results
5. 💾 Database save confirmation

## Database Location

The database will be created at: `data/mutual_funds.db`

## Troubleshooting

### Python not found
- Install Python from [python.org](https://www.python.org/downloads/)
- Or use `python3` instead of `python`
- On Windows, you may need to add Python to PATH

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if you're using the correct Python environment (virtual environment recommended)

### Scraping fails
- Check your internet connection
- Verify the URL is accessible
- The website structure may have changed - check the actual HTML structure

### Database errors
- Ensure you have write permissions in the project directory
- The `data/` folder will be created automatically

## Next Steps

After successful data extraction:

1. Review the scraped data in the database
2. Verify data accuracy
3. Add more scheme URLs to scrape
4. Proceed to build the chatbot with embeddings and RAG

