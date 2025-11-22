# UTI Mutual Fund Factual Chatbot

> A RAG-based factual information assistant for UTI Mutual Funds that provides accurate, source-attributed answers to user queries about UTI AMC schemes.

## 🎯 Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** chatbot that answers questions about UTI Mutual Funds using factual data scraped from Groww. The system combines semantic search with Google's Gemini AI to deliver accurate, traceable responses without providing investment advice.

### Key Features

- ✅ **Factual Information Only** - No investment advice, only verifiable facts
- ✅ **Source Attribution** - Every response includes Groww source URLs
- ✅ **RAG Architecture** - Semantic search over 211 data chunks with embeddings
- ✅ **35 UTI Funds Coverage** - Complete data for all major UTI schemes
- ✅ **Real-time Data** - Scraped holdings, exit loads, expense ratios, NAV, etc.
- ✅ **Mobile-First UI** - Responsive design with auto-opening sidebar
- ✅ **Smart Query Detection** - Automatically routes to appropriate data types

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │ ───> │   Flask API  │ ───> │   Gemini    │
│   (React)   │ <─── │   (Python)   │ <─── │     AI      │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├──> Sentence Transformers
                            │    (Embeddings)
                            │
                            └──> RAG Chunks JSON
                                 (211 chunks)
```

### Tech Stack

**Backend:**
- Python 3.11
- Flask + CORS
- Google Gemini API (gemini-pro)
- Sentence Transformers (all-MiniLM-L6-v2)
- BeautifulSoup4 (web scraping)

**Frontend:**
- React 18 + Vite
- TailwindCSS
- Axios

**Deployment:**
- Frontend: Vercel
- Backend: Railway

## 📁 Project Structure

```
Milestone 1/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/         # UI components (Sidebar, ChatWindow, etc.)
│   │   ├── App.jsx            # Main app component
│   │   └── index.css          # TailwindCSS styles
│   ├── vite.config.js         # Vite config with proxy
│   └── package.json
│
├── scripts/                    # Backend scripts
│   ├── gemini_web_chatbot.py  # Main Flask API server
│   ├── scrape_holdings.py     # Holdings data scraper
│   ├── scrape_exit_loads.py   # Exit load data scraper
│   ├── split_expense_chunks.py # Data chunk splitter
│   └── regenerate_embeddings.py # Embedding generator
│
├── rag_data/                   # RAG data storage
│   ├── rag_chunks.json        # 211 structured data chunks
│   └── embeddings.pkl         # Pre-computed embeddings
│
├── scraper/                    # Web scraping utilities
│   ├── groww_scraper.py       # Main scraper
│   └── validators.py          # Data validation
│
├── database/                   # SQLite database (legacy)
│   ├── models.py
│   └── db_manager.py
│
├── requirements.txt           # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Gemini API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd "Milestone 1"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv_gemini
   .venv_gemini\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Gemini API key**
   ```bash
   set GEMINI_API_KEY=your_api_key_here
   ```

5. **Run backend server**
   ```bash
   python scripts\gemini_web_chatbot.py
   ```
   Backend runs on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:3001`

4. **Open in browser**
   Navigate to `http://localhost:3001`

## 📊 Data Coverage

### 35 UTI Mutual Funds

The chatbot covers all major UTI schemes across categories:
- **Equity Funds**: Large Cap, Mid Cap, Large & Mid Cap, Flexi Cap, Focused, Value, Infrastructure, Healthcare, Consumer, Technology, MNC, etc.
- **Debt Funds**: Corporate Bond, Banking & PSU, Dynamic Bond, Short/Medium Duration, etc.
- **Hybrid Funds**: Balanced Advantage, Multi-Asset, Aggressive Hybrid
- **ELSS**: Tax Saver Fund
- **Index Funds**: Nifty, Nifty Next 50
- **Liquid & Overnight Funds**

### Data Types (211 Chunks)

**Per Fund:**
1. **Expense Information** (35 chunks)
   - Expense Ratio
   - Stamp Duty

2. **NAV/SIP Information** (35 chunks)
   - Current NAV with date
   - Minimum SIP amount
   - Exit Load details

3. **Fund Characteristics** (35 chunks)
   - Fund Size (AUM)
   - Fund Manager names
   - Scheme Type
   - Category

4. **Performance Metrics** (35 chunks)
   - P/E Ratio
   - P/B Ratio

5. **Holdings Information** (35 chunks)
   - Top 5 stock holdings
   - Percentage allocation

6. **Risk Metrics** (36 chunks)
   - Alpha, Beta, Sharpe, Sortino ratios

## ⚙️ How It Works

### RAG Pipeline

1. **User Query** → Frontend sends question to Flask API

2. **Query Embedding** → Convert question to 384-dim vector using sentence-transformers

3. **Semantic Search** → Find top relevant chunks using cosine similarity (threshold: 0.2)

4. **Smart Filtering** → Route to specific chunk types based on keywords:
   - "expense ratio" → expense_information
   - "NAV", "SIP", "exit load" → nav_sip_information
   - "fund manager", "category" → fund_characteristics
   - "P/E", "P/B" → performance_metrics
   - "holdings", "stocks" → holdings_information

5. **Context Building** → Format relevant chunks with fund name and data

6. **Gemini Generation** → Generate clean, formatted response

7. **Response** → Return answer with Groww source URLs

### Guardrails

- **Investment Advice Detection**: Blocks queries asking for recommendations
- **Greeting Handler**: Responds to "Hi"/"Hello" with welcome message
- **Unknown Info Handler**: Returns "I don't have this information" for missing data

## 📝 Example Queries

**Expense & Costs:**
- "What is the expense ratio of UTI ELSS Tax Saver Fund?"
- "Stamp duty for UTI Nifty Index Fund?"

**NAV & Investment:**
- "What is NAV of UTI Large & Mid Cap Fund Direct Growth?"
- "Minimum SIP for UTI Infrastructure Fund?"
- "Exit Load of UTI Healthcare Fund?"

**Fund Details:**
- "Who is the fund manager of UTI MNC Fund Direct Growth?"
- "What is the scheme type of UTI Value Fund?"
- "Fund size of UTI Flexi Cap Fund?"

**Performance:**
- "What is the P/E ratio of UTI India Consumer Fund Direct Growth?"
- "P/B ratio of UTI Technology Fund?"

**Holdings:**
- "What are the top holdings of UTI Nifty Index Fund?"
- "Show me holdings of UTI Large Cap Fund?"

## 🛠️ Development

### Data Scraping

**Scrape Holdings Data:**
```bash
python scripts\scrape_holdings.py
```

**Scrape Exit Loads:**
```bash
python scripts\scrape_exit_loads.py
```

**Regenerate Embeddings:**
```bash
python scripts\regenerate_embeddings.py
```

### Data Structure

**rag_chunks.json** format:
```json
{
  "expense_information": [
    {
      "fund_name": "UTI Large & Mid Cap Fund Direct Growth",
      "chunk_type": "expense_information",
      "data": {
        "expense_ratio": "0.97%",
        "stamp_duty": "0.005%"
      },
      "source_url": "https://groww.in/mutual-funds/..."
    }
  ],
  "nav_sip_information": [...],
  "fund_characteristics": [...],
  "performance_metrics": [...],
  "holdings_information": [...]
}
```

## 🚀 Deployment

### Production URLs

- **Frontend**: Deployed on Vercel
- **Backend**: Deployed on Railway at `https://mutualfundchatbot-production.up.railway.app`

### Environment Variables

**Backend (Railway):**
```
GEMINI_API_KEY=your_gemini_api_key
```

**Frontend (Vercel):**
```
VITE_API_URL=https://mutualfundchatbot-production.up.railway.app
```

### Deploy Commands

```bash
# Commit changes
git add .
git commit -m "Your message"

# Push to deploy (auto-deploys to Vercel and Railway)
git push origin main
```

## 📱 Mobile Features

- **Fixed Header**: Always visible at top of viewport
- **Auto-open Sidebar**: Opens automatically on first mobile visit (tracked via localStorage `chat_side_seen`)
- **Close Button**: Visible only on mobile view
- **Responsive Design**: Adapts to all screen sizes

## 📜 API Reference

### POST /ask

**Request:**
```json
{
  "question": "What is the expense ratio of UTI ELSS Tax Saver Fund?"
}
```

**Response:**
```json
{
  "response": "UTI ELSS Tax Saver Fund Direct Growth\nExpense Ratio: 0.91%\nStamp Duty: 0.005%\nSource: https://groww.in/mutual-funds/...",
  "sources": [
    {
      "fund_name": "UTI ELSS Tax Saver Fund Direct Growth",
      "url": "https://groww.in/mutual-funds/...",
      "type": "expense information"
    }
  ]
}
```

## ⚠️ Important Notes

## ⚠️ Important Notes

- **This is a factual information chatbot only** - Does NOT provide investment advice or recommendations
- **Source Attribution**: Every response includes Groww source URLs for verification
- **Data Freshness**: NAV data is as of the last scrape (check NAV date in responses)
- **Rate Limiting**: Scrapers use 2-second delays to respect Groww's servers
- **Educational Purpose**: Please respect Groww's terms of service

## 🛡️ Disclaimer

This chatbot provides **factual information only** about UTI Mutual Funds. It does not:
- Provide investment advice or recommendations
- Suggest which funds to buy or sell
- Analyze portfolio suitability
- Guarantee data accuracy (always verify from official sources)

**For investment decisions, please consult a certified financial advisor.**

## 📝 License

This project is for educational purposes only.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Improve documentation
- Add support for more AMCs

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Built with ❤️ using RAG, Gemini AI, and React**

