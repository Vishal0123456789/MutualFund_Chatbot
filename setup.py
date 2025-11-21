"""
Setup script for UTI Mutual Fund FAQ Assistant
"""

from setuptools import setup, find_packages

setup(
    name="uti-faq-assistant",
    version="0.1.0",
    description="FAQ Assistant for UTI Mutual Fund schemes",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "pandas>=2.1.3",
        "sqlalchemy>=2.0.23",
        "lxml>=4.9.3",
        "validators>=0.22.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
)

