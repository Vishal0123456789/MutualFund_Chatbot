# Enhanced FAQ Assistant / Chatbot

This project provides multiple interfaces for an FAQ assistant that can answer questions about UTI mutual funds.

## Components

1. **Console-based Interactive FAQ Assistant** - Basic command-line interface
2. **LLM-Enhanced Chatbot** - Advanced chatbot with optional OpenAI integration
3. **Web-based Chatbot** - Browser interface with HTML/CSS/JavaScript frontend

## Prerequisites

Make sure you have run the data collection and preparation steps:

```bash
# Run the scraper (if not already done)
python scripts/scrape_uti_schemes.py

# Prepare data for RAG (if not already done)
python scripts/prepare_rag_data.py
```

Install required dependencies:

```bash
# For basic functionality
pip install sentence-transformers scikit-learn numpy

# For web interface
pip install flask

# For LLM integration (optional)
pip install openai
```

## Running the Chatbots

### 1. Console-based Interactive FAQ Assistant

```bash
python scripts/faq_assistant.py
```

Features:
- Ask questions about UTI mutual funds
- Get formatted responses with source attribution
- Session summary statistics

### 2. LLM-Enhanced Chatbot

```bash
# Set OpenAI API key (optional, for enhanced responses)
export OPENAI_API_KEY=your_api_key_here

python scripts/llm_enhanced_chatbot.py
```

Features:
- Natural language responses using LLM (if API key provided)
- Fallback to basic responses without API key
- Session tracking and statistics

### 3. Web-based Chatbot

```bash
python scripts/web_chatbot.py
```

Then open your browser to http://localhost:5000

Features:
- Web interface with chat UI
- Real-time responses
- Source attribution with clickable links
- Responsive design

## Example Questions

Try asking questions like:
- "What is the expense ratio of UTI ELSS Tax Saver Fund?"
- "What is the risk level of UTI Small Cap Fund?"
- "How can I download my transaction history from Groww?"
- "What is the benchmark for UTI Nifty 50 Index Fund?"

## Data Sources

The assistant uses data scraped from:
- UTI Mutual Fund websites
- Groww platform help documentation

All information includes proper source attribution.