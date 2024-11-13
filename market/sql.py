import sqlite3
import pandas as pd
from datetime import datetime
import numpy as np

class FinancialDatabase:
    def __init__(self, db_path='financial_statements.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Create necessary tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            # Create tables for each statement type
            conn.execute('''
                CREATE TABLE IF NOT EXISTS financial_data (
                    ticker TEXT,
                    statement_type TEXT,
                    metric_name TEXT,
                    date TEXT,
                    value REAL,
                    last_updated TIMESTAMP,
                    PRIMARY KEY (ticker, statement_type, metric_name, date)
                )
            ''')
            
            # Create table to track last update for each ticker
            conn.execute('''
                CREATE TABLE IF NOT EXISTS update_log (
                    ticker TEXT PRIMARY KEY,
                    last_updated TIMESTAMP
                )
            ''')
          
    def update_financial_data(self, ticker_symbol, statements):
        """Update financial data for a given ticker"""
        #ticker = yf.Ticker(ticker_symbol)
        current_time = datetime.now()
        
        # Get all financial statements
        #statements = {
        #    'Balance Sheet': ticker.balance_sheet,
        #    'Income Statement': ticker.income_stmt,
        #    'Cash Flow': ticker.cash_flow
        #}
        
        with sqlite3.connect(self.db_path) as conn:
            for statement_type, df in statements.items():
                if df is None or df.empty:
                    continue
                    
                # Convert dates to string format for consistent storage
                df.columns = df.columns.strftime('%Y-%m-%d')
                
                # Process each metric in the statement
                for metric_name in df.index:
                    for date, value in df.loc[metric_name].items():
                        # Convert numpy/pandas types to Python native types
                        if isinstance(value, (np.integer, np.floating)):
                            value = float(value)
                        
                        # Insert or update the value
                        conn.execute('''
                            INSERT OR REPLACE INTO financial_data 
                            (ticker, statement_type, metric_name, date, value, last_updated)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (ticker_symbol, statement_type, metric_name, date, value, current_time))
            
            # Update the log
            conn.execute('''
                INSERT OR REPLACE INTO update_log (ticker, last_updated)
                VALUES (?, ?)
            ''', (ticker_symbol, current_time))
    
    def get_financial_data(self, ticker_symbol, statement_type=None, start_date=None, end_date=None):
        """Retrieve financial data from database"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT metric_name, date, value
                FROM financial_data
                WHERE ticker = ?
            '''
            params = [ticker_symbol]
            
            if statement_type:
                query += ' AND statement_type = ?'
                params.append(statement_type)
            
            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)
            
            # Get the data and pivot it to match the original DataFrame format
            df = pd.read_sql_query(query, conn, params=params)
            if not df.empty:
                pivoted = df.pivot(index='metric_name', columns='date', values='value')
                return pivoted
            return pd.DataFrame()
    
    def get_last_update(self, ticker_symbol):
        """Get the last update time for a ticker"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT last_updated FROM update_log WHERE ticker = ?',
                (ticker_symbol,)
            )
            result = cursor.fetchone()
            return result[0] if result else None    