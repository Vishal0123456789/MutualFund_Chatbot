"""
Database manager for storing and retrieving scraped data
"""

import json
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from typing import Dict, Optional, List
from datetime import datetime

from database.models import Base, Scheme, SchemeData, ScrapeLog


class DatabaseManager:
    """Manages database operations for scraped data"""
    
    def __init__(self, db_path: str = 'data/mutual_funds.db'):
        """
        Initialize database manager
        Args:
            db_path: Path to SQLite database file
        """
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_scheme_data(self, scraped_data: Dict, validation_result: Dict) -> Optional[int]:
        """
        Save scraped data to database
        Args:
            scraped_data: Dictionary containing scraped data
            validation_result: Validation result from DataValidator
        Returns:
            scheme_id if successful, None otherwise
        """
        session = self.Session()
        
        try:
            # Check if scheme already exists
            scheme = session.query(Scheme).filter_by(
                source_url=scraped_data['source_url']
            ).first()
            
            if scheme:
                scheme.scheme_name = scraped_data.get('fund_name', scheme.scheme_name)
                scheme.updated_at = datetime.utcnow()
                scheme_id = scheme.id
            else:
                # Create new scheme
                scheme = Scheme(
                    scheme_name=scraped_data.get('fund_name', 'Unknown'),
                    source_url=scraped_data['source_url'],
                    fund_house='UTI'
                )
                session.add(scheme)
                session.flush()
                scheme_id = scheme.id
            
            # Save individual data points
            data_mapping = {
                'nav': scraped_data.get('nav'),
                'min_sip': scraped_data.get('min_sip'),
                'fund_size': scraped_data.get('fund_size'),
                'pe_ratio': scraped_data.get('pe_ratio'),
                'pb_ratio': scraped_data.get('pb_ratio'),
                'fund_returns': scraped_data.get('fund_returns'),
                'category_averages': scraped_data.get('category_averages'),
                'rank': scraped_data.get('rank'),
                'expense_ratio': scraped_data.get('expense_ratio'),
                'exit_load': scraped_data.get('exit_load'),
                'stamp_duty': scraped_data.get('stamp_duty'),
                'fund_manager': scraped_data.get('fund_manager'),
                'lock_in': scraped_data.get('lock_in'),
                'scheme_type': scraped_data.get('scheme_type'),
                'sub_category': scraped_data.get('sub_category'),
                'is_elss': scraped_data.get('is_elss'),
                'category_label': scraped_data.get('category_label'),
                'annualised_returns': scraped_data.get('annualised_returns'),
                'holdings': scraped_data.get('holdings'),
                'risk_metrics': scraped_data.get('risk_metrics'),
                'riskometer': scraped_data.get('riskometer'),
                'benchmark': scraped_data.get('benchmark'),
                'statement_download_info': scraped_data.get('statement_download_info'),
            }
            
            data_count = 0
            for data_type, value in data_mapping.items():
                if value is not None:
                    # Convert complex data to JSON string
                    if isinstance(value, (dict, list)):
                        value_str = json.dumps(value)
                    else:
                        value_str = str(value)
                    
                    # Check if data point already exists
                    existing_data = session.query(SchemeData).filter(
                        and_(
                            SchemeData.scheme_id == scheme_id,
                            SchemeData.data_type == data_type
                        )
                    ).first()
                    
                    if existing_data:
                        existing_data.value = value_str
                        existing_data.scraped_at = datetime.utcnow()
                    else:
                        new_data = SchemeData(
                            scheme_id=scheme_id,
                            data_type=data_type,
                            value=value_str,
                            source_url=scraped_data['source_url']
                        )
                        session.add(new_data)
                    
                    data_count += 1
            
            # Log scraping activity
            status = 'success' if validation_result['is_valid'] else 'partial'
            if validation_result['errors']:
                status = 'failed'
            
            log = ScrapeLog(
                scheme_url=scraped_data['source_url'],
                status=status,
                errors=json.dumps(validation_result.get('errors', [])),
                warnings=json.dumps(validation_result.get('warnings', [])),
                data_count=data_count
            )
            session.add(log)
            
            session.commit()
            return scheme_id
            
        except IntegrityError as e:
            session.rollback()
            print(f"Database integrity error: {e}")
            return None
        except Exception as e:
            session.rollback()
            print(f"Error saving data: {e}")
            return None
        finally:
            session.close()
    
    def get_scheme_data(self, scheme_url: str) -> Optional[Dict]:
        """
        Retrieve all data for a scheme
        Args:
            scheme_url: Source URL of the scheme
        Returns:
            Dictionary containing all scheme data
        """
        session = self.Session()
        
        try:
            scheme = session.query(Scheme).filter_by(source_url=scheme_url).first()
            if not scheme:
                return None
            
            data_points = session.query(SchemeData).filter_by(scheme_id=scheme.id).all()
            
            result = {
                'scheme_id': scheme.id,
                'scheme_name': scheme.scheme_name,
                'source_url': scheme.source_url,
                'data': {}
            }
            
            for dp in data_points:
                # Try to parse JSON, otherwise return as string
                try:
                    result['data'][dp.data_type] = json.loads(dp.value)
                except json.JSONDecodeError:
                    result['data'][dp.data_type] = dp.value
            
            return result
            
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return None
        finally:
            session.close()
    
    def get_all_schemes(self) -> List[Dict]:
        """Get list of all schemes"""
        session = self.Session()
        
        try:
            schemes = session.query(Scheme).all()
            return [
                {
                    'id': s.id,
                    'scheme_name': s.scheme_name,
                    'source_url': s.source_url,
                    'updated_at': s.updated_at.isoformat() if s.updated_at else None
                }
                for s in schemes
            ]
        except Exception as e:
            print(f"Error retrieving schemes: {e}")
            return []
        finally:
            session.close()

