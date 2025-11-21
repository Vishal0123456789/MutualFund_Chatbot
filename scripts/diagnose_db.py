"""
Diagnostic script to check database contents
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager


def diagnose_database():
    """Diagnose database contents"""
    print("Checking database contents...")
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager('data/mutual_funds.db')
        
        # Get all schemes
        schemes = db_manager.get_all_schemes()
        
        print(f"Found {len(schemes)} schemes in database:")
        
        if schemes:
            for scheme in schemes:
                print(f"  - {scheme['scheme_name']}")
                print(f"    URL: {scheme['source_url']}")
                print(f"    ID: {scheme['id']}")
                
                # Get scheme data
                scheme_data = db_manager.get_scheme_data(scheme['source_url'])
                if scheme_data:
                    print(f"    Data points: {len(scheme_data['data'])}")
                    # Show some key data points
                    key_points = ['expense_ratio', 'exit_load', 'min_sip', 'riskometer', 'benchmark']
                    for point in key_points:
                        if point in scheme_data['data']:
                            print(f"      {point}: {scheme_data['data'][point]}")
                print()
        else:
            print("No schemes found in database.")
            
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    diagnose_database()