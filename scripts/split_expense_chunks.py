"""
Split expense_information chunks into two types:
1. nav_sip_information: NAV, min_sip, exit_load
2. expense_information: expense_ratio, stamp_duty
"""
import json
from pathlib import Path

def main():
    # Load existing RAG chunks
    rag_file = Path(__file__).parent.parent / 'rag_data' / 'rag_chunks.json'
    with open(rag_file, 'r', encoding='utf-8') as f:
        rag_data = json.load(f)
    
    print("Splitting expense_information chunks...")
    print("=" * 60)
    
    # Create new chunk types
    nav_sip_chunks = []
    expense_chunks = []
    
    for chunk in rag_data['expense_information']:
        fund_name = chunk['fund_name']
        source_url = chunk['source_url']
        data = chunk['data']
        
        # Create NAV/SIP/Exit Load chunk
        nav_sip_data = {}
        if 'nav' in data:
            nav_sip_data['nav'] = data['nav']
        if 'nav_date' in data:
            nav_sip_data['nav_date'] = data['nav_date']
        if 'min_sip' in data:
            nav_sip_data['min_sip'] = data['min_sip']
        if 'exit_load' in data:
            nav_sip_data['exit_load'] = data['exit_load']
        
        if nav_sip_data:
            nav_sip_chunks.append({
                "fund_name": fund_name,
                "source_url": source_url,
                "chunk_type": "nav_sip_information",
                "data": nav_sip_data
            })
        
        # Create Expense/Stamp Duty chunk
        expense_data = {}
        if 'expense_ratio' in data:
            expense_data['expense_ratio'] = data['expense_ratio']
        if 'stamp_duty' in data:
            expense_data['stamp_duty'] = data['stamp_duty']
        
        if expense_data:
            expense_chunks.append({
                "fund_name": fund_name,
                "source_url": source_url,
                "chunk_type": "expense_information",
                "data": expense_data
            })
        
        print(f"✅ Split: {fund_name}")
    
    # Replace in rag_data
    rag_data['nav_sip_information'] = nav_sip_chunks
    rag_data['expense_information'] = expense_chunks
    
    # Save updated data
    with open(rag_file, 'w', encoding='utf-8') as f:
        json.dump(rag_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Splitting complete!")
    print(f"Created {len(nav_sip_chunks)} nav_sip_information chunks")
    print(f"Created {len(expense_chunks)} expense_information chunks")
    print(f"Saved to: {rag_file}")
    print("\nNext steps:")
    print("1. Update gemini_web_chatbot.py to handle nav_sip_information chunk type")
    print("2. Run regenerate_embeddings.py")
    print("3. Restart the backend")

if __name__ == "__main__":
    main()
