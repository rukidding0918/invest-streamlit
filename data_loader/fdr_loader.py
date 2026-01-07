import FinanceDataReader as fdr
import pandas as pd
from .base import DataLoader

class FdrLoader(DataLoader):
    SYMBOL_MAP = {
        "KOSPI": "^KS11",
        "KOSDAQ": "^KQ11",
        "S&P 500": "US500",
        "NASDAQ": "IXIC",
        "Dow Jones": "DJI",
        "Nikkei 225": "N225",
    }

    def get_index_ohlcv(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # Map the readable name to FDR symbols
        fdr_symbol = self.SYMBOL_MAP.get(symbol, symbol)
        
        # FDR handles YYYY-MM-DD or YYYYMMDD
        try:
            df = fdr.DataReader(fdr_symbol, start=start_date, end=end_date)
        except Exception:
            # Fallback to direct symbol if mapping fails
            df = fdr.DataReader(symbol, start=start_date, end=end_date)
            
        # Rename FDR columns to match pykrx style
        rename_map = {
            "Open": "시가",
            "High": "고가",
            "Low": "저가",
            "Close": "종가",
            "Volume": "거래량",
        }
        df = df.rename(columns=rename_map)
        return df

    def get_vix_history(self, start_date: str, end_date: str) -> pd.DataFrame:
        return fdr.DataReader("^VIX", start=start_date, end=end_date)

    def get_etf_list(self) -> pd.DataFrame:
        etf_list = fdr.StockListing('ETF/KR')
        
        # 제외 키워드
        exclude_keywords = ['인버스', '레버리지', r'\(H\)']
        
        # 필터링 (regex=True 명시, 괄호 이스케이프)
        mask = ~etf_list['Name'].str.contains('|'.join(exclude_keywords), regex=True, na=False)
        filtered_etf = etf_list[mask]
        
        # Volume 정렬
        filtered_etf = filtered_etf.sort_values('Volume', ascending=False)
        
        return filtered_etf
