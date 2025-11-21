"""
Robust Gemini Chatbot with better error handling and fallbacks
"""

import sys
import json
import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import Google Generative AI with better error handling
GOOGLE_AI_AVAILABLE = False
genai = None

try:
    import google.generativeai as genai_module
    genai = genai_module
    GOOGLE_AI_AVAILABLE = True
    print("Google Generative AI library loaded successfully")
except ImportError as e:
    print("Google Generative AI library not found. Install with: pip install google-generativeai")
    print("Falling back to basic response generation.")
except Exception as e:
    print(f"Google Generative AI library error: {e}")
    print("Falling back to basic response generation.")

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class RobustGeminiChatbot:
    def __init__(self, rag_data_path='rag_data/rag_chunks.json', embeddings_path='rag_data/embeddings.pkl', api_key=None):
        """Initialize robust Gemini chatbot with RAG data"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rag_data_path = rag_data_path
        self.embeddings_path = embeddings_path
        self.chunks = []
        self.embeddings = []
        self.conversation_history = []
        self.session_start = datetime.now()
        
        # Google Generative AI setup with better error handling
        self.gemini_model = None
        self.api_key = api_key
        
        if GOOGLE_AI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                # Try different models in order of preference
                models_to_try = ['gemini-1.5-flash-latest', 'gemini-pro', 'gemini-1.5-pro-latest']
                for model_name in models_to_try:
                    try:
                        self.gemini_model = genai.GenerativeModel(model_name)
                        print(f"Gemini integration enabled with {model_name} model")
                        break
                    except Exception as e:
                        print(f"Failed to initialize {model_name}: {e}")
                        continue
                
                if not self.gemini_model:
                    print("Could not initialize any Gemini model, falling back to basic response generation")
            except Exception as e:
                print(f"Error configuring Gemini: {e}")
                print("Falling back to basic response generation.")
        elif GOOGLE_AI_AVAILABLE:
            print("Google Generative AI library available but no API key provided")
            print("Set GOOGLE_API_KEY environment variable for LLM integration")
        else:
            print("Google Generative AI library not available, using basic response generation")
        
        self.load_and_prepare_data()
    
    def load_and_prepare_data(self):
        """Load RAG data and prepare embeddings"""
        print("Loading RAG data...")
        
        # Load chunks from JSON
        with open(self.rag_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten all chunks into a single list
        for category_chunks in data.values():
            self.chunks.extend(category_chunks)
        
        print(f"Loaded {len(self.chunks)} chunks")
        
        # Load embeddings from disk
        print("Loading embeddings from disk...")
        try:
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
            print("Embeddings loaded successfully")
        except Exception as e:
            print(f"Error loading embeddings: {e}")
            print("Creating new embeddings...")
            self.create_embeddings()
    
    def create_embeddings(self):
        """Create embeddings for all chunks"""
        print("Creating embeddings for all chunks...")
        texts = []
        for chunk in self.chunks:
            # Create a text representation of the chunk
            text_parts = [f"Fund: {chunk['fund_name']}"]
            text_parts.append(f"Category: {chunk['chunk_type']}")
            for key, value in chunk['data'].items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        text_parts.append(f"{key} {sub_key}: {sub_value}")
                else:
                    text_parts.append(f"{key}: {value}")
            texts.append(" ".join(text_parts))
        
        # Create embeddings
        self.embeddings = self.model.encode(texts)
        print("Embeddings created successfully")
    
    def find_relevant_chunks(self, question: str, top_k: int = 3) -> List[Dict]:
        """Find most relevant chunks for a given question"""
        # Create embedding for the question
        question_embedding = self.model.encode([question])
        
        # Calculate similarities
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold to filter out irrelevant chunks
                results.append({
                    'chunk': self.chunks[idx],
                    'similarity': similarities[idx]
                })
        
        return results
    
    def format_context_for_llm(self, relevant_chunks: List[Dict]) -> str:
        """Format context for LLM prompt"""
        if not relevant_chunks:
            return "No relevant information found."
        
        context_parts = []
        context_parts.append("Relevant information about UTI mutual funds:")
        
        for i, result in enumerate(relevant_chunks, 1):
            chunk = result['chunk']
            context_parts.append(f"\n{i}. Fund: {chunk['fund_name']}")
            context_parts.append(f"   Category: {chunk['chunk_type'].replace('_', ' ').title()}")
            
            # Add the data
            for key, value in chunk['data'].items():
                formatted_key = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    context_parts.append(f"   {formatted_key}:")
                    for sub_key, sub_value in value.items():
                        context_parts.append(f"     {sub_key.title()}: {sub_value}")
                else:
                    context_parts.append(f"   {formatted_key}: {value}")
            
            # Add source
            context_parts.append(f"   Source: {chunk['source_url']}")
        
        return "\n".join(context_parts)
    
    def generate_gemini_response(self, question: str, context: str) -> str:
        """Generate response using Gemini"""
        if not self.gemini_model:
            # Fallback to basic response generation
            return self.generate_basic_response(question, context)
        
        try:
            # Create prompt for Gemini
            prompt = f"""
You are a helpful assistant answering questions about UTI mutual funds. 
Use the following context to answer the question accurately and concisely.

Context:
{context}

Question: {question}

Please provide a helpful, conversational response based on the context above. 
If the context doesn't contain relevant information, politely say so.
Format your response in a clear, easy-to-read manner.
This is for factual information only. Do not provide investment advice.

Response:
"""

            # Call Gemini API with timeout
            import asyncio
            try:
                # Try async version first
                response = self.gemini_model.generate_content(prompt, timeout=30)
            except:
                # Fallback to sync version
                response = self.gemini_model.generate_content(prompt)
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            # Fallback to basic response
            return self.generate_basic_response(question, context)
    
    def generate_basic_response(self, question: str, context: str) -> str:
        """Generate basic response when LLM is not available"""
        # Extract key information from context
        lines = context.split('\n')
        if len(lines) > 10:
            # Truncate for readability
            context_summary = '\n'.join(lines[:10]) + "\n... (more information available)"
        else:
            context_summary = context
        
        return f"""Based on the information I found:

{context_summary}"""
    
    def chat(self, question: str) -> str:
        """Handle a chat interaction"""
        print(f"\nQuestion: {question}")
        
        # Find relevant chunks
        relevant_chunks = self.find_relevant_chunks(question)
        
        # Format context
        context = self.format_context_for_llm(relevant_chunks)
        
        # Generate response
        if self.gemini_model and self.api_key:
            response = self.generate_gemini_response(question, context)
        else:
            response = self.generate_basic_response(question, context)
        
        # Add to conversation history
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'response': response,
            'chunks_found': len(relevant_chunks),
            'used_llm': bool(self.gemini_model and self.api_key)
        })
        
        return response
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        duration = datetime.now() - self.session_start
        minutes = duration.total_seconds() / 60
        
        llm_usage = sum(1 for interaction in self.conversation_history if interaction.get('used_llm', False))
        
        return f"""
Session Summary:
- Duration: {minutes:.1f} minutes
- Questions asked: {len(self.conversation_history)}
- LLM-enhanced responses: {llm_usage}
- Basic responses: {len(self.conversation_history) - llm_usage}
- Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
        """


def main():
    """Main function to run robust Gemini chatbot"""
    print("Starting Robust Gemini Chatbot...")
    print("Loading data and embeddings...")
    
    # Try to get Google API key from environment
    import os
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    # Initialize chatbot
    chatbot = RobustGeminiChatbot(api_key=api_key)
    
    print("\n" + "="*80)
    print("Robust Gemini Chatbot Ready!")
    print("="*80)
    if api_key and chatbot.gemini_model:
        print("✅ Gemini integration enabled")
    else:
        print("ℹ️  Using basic response generation")
        if not api_key:
            print("   To enable LLM features, set GOOGLE_API_KEY environment variable")
    print("\nAsk questions about UTI mutual funds, or type 'quit' to exit.")
    print("Type 'summary' to see session statistics.")
    print("\nExample questions:")
    print("  - What is the expense ratio of UTI ELSS Tax Saver Fund?")
    print("  - What is the risk level of UTI Small Cap Fund?")
    print("  - How can I download my transaction history from Groww?")
    print("  - What is the benchmark for UTI Nifty 50 Index Fund?")
    print("="*80)
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nChatbot: Thank you for using the chatbot! Here's your session summary:")
                print(chatbot.get_session_summary())
                print("Goodbye!")
                break
            
            if question.lower() == 'summary':
                print("\nChatbot:", chatbot.get_session_summary())
                continue
            
            if not question:
                continue
                
            answer = chatbot.chat(question)
            print(f"\nChatbot:\n{answer}")
            
        except KeyboardInterrupt:
            print("\n\nChatbot: Thank you for using the chatbot! Here's your session summary:")
            print(chatbot.get_session_summary())
            print("Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()