"""
Database models for storing mutual fund data
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class Scheme(Base):
    """Table to store scheme information"""
    __tablename__ = 'schemes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_name = Column(String(500), nullable=False)
    scheme_code = Column(String(100), unique=True, nullable=True)
    fund_house = Column(String(100), default='UTI')
    source_url = Column(String(1000), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to data points
    data_points = relationship("SchemeData", back_populates="scheme", cascade="all, delete-orphan")


class SchemeData(Base):
    """Table to store individual data points for each scheme"""
    __tablename__ = 'scheme_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(Integer, ForeignKey('schemes.id'), nullable=False)
    data_type = Column(String(100), nullable=False)  # e.g., 'nav', 'expense_ratio', 'fund_returns'
    value = Column(Text, nullable=False)  # JSON string for complex data
    source_url = Column(String(1000), nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to scheme
    scheme = relationship("Scheme", back_populates="data_points")
    
    # Unique constraint on scheme_id and data_type
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class ScrapeLog(Base):
    """Table to log scraping activities"""
    __tablename__ = 'scrape_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_url = Column(String(1000), nullable=False)
    status = Column(String(50), nullable=False)  # 'success', 'failed', 'partial'
    errors = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    data_count = Column(Integer, default=0)  # Number of data points extracted

