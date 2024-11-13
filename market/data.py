import yfinance as yf
import pandas as pd
from plotly import graph_objects as go
from datetime import date
from market.sql import FinancialDatabase


class MarketData:
    def __init__(self):
        self.fd = FinancialDatabase()

    def get_stock(self):
        # Parameters for retrieving the stock data
        start_date = "2015-01-01"
        end_date = date.today().strftime("%Y-%m-%d")
        selected_stock = 'AAPL'

        data = self.get_stock_data(selected_stock, start_date, end_date)
        return data

    def get_stock_data(self, ticker, start, end):
        # downloading the stock data from START to TODAY
        ticker_data = yf.download(ticker, start, end)
        ticker_data.reset_index(inplace=True)  # put date in the first column
        ticker_data['Date'] = pd.to_datetime(
            ticker_data['Date']).dt.tz_localize(None)
        return ticker_data

    def get_data_from_range(self, state):
        print("GENERATING HIST DATA")
        start_date = state.start_date if type(
            state.start_date) == str else state.start_date.strftime("%Y-%m-%d")
        end_date = state.end_date if type(
            state.end_date) == str else state.end_date.strftime("%Y-%m-%d")

        state.data = get_stock_data(state.selected_stock, start_date, end_date)
        if len(state.data) == 0:
            notify(state, "error", f"Not able to download data {
                   state.selected_stock} from {start_date} to {end_date}")
            return
        notify(state, 's', 'Historical data has been updated!')
        notify(state, 'w', 'Deleting previous predictions...')
        state.forecast = pd.DataFrame(columns=['Date', 'Lower', 'Upper'])

    def create_candlestick_chart(self, data):
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=data['Date'],
                                     open=data['Open'],
                                     high=data['High'],
                                     low=data['Low'],
                                     close=data['Close'],
                                     name='Candlestick'))
        fig.update_layout(margin=dict(l=30, r=30, b=30, t=30),
                          xaxis_rangeslider_visible=False)
        return fig

    def get_basic_fundamentals(self, ticker_symbol):
        """
        Get basic fundamental data for a given ticker symbol
        Returns a dictionary of key financial metrics
        """
        # Create a Ticker object
        ticker = yf.Ticker(ticker_symbol)

        # Get key financial metrics from info
        fundamentals = {
            'Enterprise Value': ticker.info.get('enterpriseValue'),
            'EBITDA': ticker.info.get('ebitda'),
            'Revenue': ticker.info.get('totalRevenue'),
            'Gross Profits': ticker.info.get('grossProfits'),
            'Total Cash': ticker.info.get('totalCash'),
            'Total Debt': ticker.info.get('totalDebt'),
            'Market Cap': ticker.info.get('marketCap'),
            'PE Ratio': ticker.info.get('forwardPE'),
            'Book Value': ticker.info.get('bookValue'),
            'Free Cash Flow': ticker.info.get('freeCashflow')
        }

        return fundamentals

    def get_detailed_financials(self, ticker_symbol):
        """
        Get detailed financial statements including balance sheet, income statement, and cash flow
        Returns a dictionary containing DataFrames of financial statements
        """
        ticker = yf.Ticker(ticker_symbol)

        financials = {
            'Balance Sheet': ticker.balance_sheet,
            'Income Statement': ticker.income_stmt,
            'Cash Flow': ticker.cash_flow
        }

        self.fd.update_financial_data(ticker_symbol, financials)

        return financials

    def get_quarterly_ratios(self, ticker_symbol):
        """
        Get quarterly financial ratios and metrics
        Returns a DataFrame of quarterly metrics
        """
        ticker = yf.Ticker(ticker_symbol)

        # Get quarterly financial ratios
        quarterly_data = pd.DataFrame({
            'Quick Ratio': ticker.quarterly_financials.loc['Quick Ratio'] if 'Quick Ratio' in ticker.quarterly_financials.index else None,
            'Current Ratio': ticker.quarterly_financials.loc['Current Ratio'] if 'Current Ratio' in ticker.quarterly_financials.index else None,
            'Debt to Equity': ticker.quarterly_financials.loc['Debt To Equity'] if 'Debt To Equity' in ticker.quarterly_financials.index else None,
            'Gross Margin': ticker.quarterly_financials.loc['Gross Margin'] if 'Gross Margin' in ticker.quarterly_financials.index else None,
            'Operating Margin': ticker.quarterly_financials.loc['Operating Margin'] if 'Operating Margin' in ticker.quarterly_financials.index else None
        })

        return quarterly_data

    def compare_quarterly_financials(self, ticker_symbol):
        """
        Compare quarterly financial metrics for the past 8 quarters
        Returns a DataFrame with quarterly comparisons
        """
        # Create a Ticker object
        ticker = yf.Ticker(ticker_symbol)

        # Get quarterly financial statements
        income_stmt = ticker.quarterly_income_stmt
        balance_sheet = ticker.quarterly_balance_sheet
        cash_flow = ticker.quarterly_cash_flow

        # Initialize DataFrame with dates from income statement
        quarters = income_stmt.columns[-20:]  # Get last 8 quarters

        # Create a dictionary to store our metrics
        quarterly_metrics = {}

        # Income Statement Metrics
        if not income_stmt.empty:
            metrics_to_get = [
                'Total Revenue',
                'Gross Profit',
                'Operating Income',
                'EBITDA',
                'Net Income',
            ]

            for metric in metrics_to_get:
                if metric in income_stmt.index:
                    quarterly_metrics[metric] = income_stmt.loc[metric, quarters]

        # Balance Sheet Metrics
        if not balance_sheet.empty:
            balance_metrics = [
                'Total Assets',
                'Total Liabilities',
                'Total Cash',
                'Total Debt',
                'Stockholders Equity'
            ]

            for metric in balance_metrics:
                if metric in balance_sheet.index:
                    quarterly_metrics[metric] = balance_sheet.loc[metric, quarters]

        # Cash Flow Metrics
        if not cash_flow.empty:
            cash_metrics = [
                'Operating Cash Flow',
                'Free Cash Flow',
                'Capital Expenditure'
            ]

            for metric in cash_metrics:
                if metric in cash_flow.index:
                    quarterly_metrics[metric] = cash_flow.loc[metric, quarters]

        # Create DataFrame from our metrics
        df = pd.DataFrame(quarterly_metrics).T

        # Calculate quarter-over-quarter growth
        qoq_growth = df.pct_change(axis=1) * 100
        qoq_growth.columns = [f'QoQ Growth {
            col:%Y-Q%q}' for col in qoq_growth.columns]

        # Calculate year-over-year growth
        yoy_growth = df.pct_change(periods=4, axis=1) * 100
        yoy_growth.columns = [f'YoY Growth {
            col:%Y-Q%q}' for col in yoy_growth.columns]

        # Format the original values in millions
        df = df / 1_000_000
        df.columns = [f'{col:%Y-Q%q}' for col in df.columns]

        return {
            'values': df,
            'qoq_growth': qoq_growth,
            'yoy_growth': yoy_growth
        }

    def format_financial_analysis(self, ticker_symbol):
        """
        Format and display the quarterly financial analysis in a readable way
        """
        results = self.compare_quarterly_financials(ticker_symbol)

        print(f"\nQuarterly Financial Analysis for {ticker_symbol}")
        print("\nValues (in millions USD)")
        print(results['values'].round(2))

        print("\nQuarter-over-Quarter Growth (%)")
        print(results['qoq_growth'].round(2))

        print("\nYear-over-Year Growth (%)")
        print(results['yoy_growth'].round(2))
