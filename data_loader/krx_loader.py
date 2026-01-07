from pykrx import stock
import FinanceDataReader as fdr
import pandas as pd
from .base import DataLoader

class PyKrxLoader(DataLoader):
    SYMBOL_MAP = {
        "KOSPI": "1001",
        "KOSDAQ": "2001",
    }

    def get_index_ohlcv(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        # pykrx uses YYYYMMDD
        start = start_date.replace("-", "")
        end = end_date.replace("-", "")
        
        # Map readable name to pykrx ticker
        krx_symbol = self.SYMBOL_MAP.get(symbol)
        if not krx_symbol:
            # If it's not a KRX index, pykrx can't handle it
            raise ValueError(f"PyKrx does not support index: {symbol}. Please use 'fdr' as source.")

        df = stock.get_index_ohlcv_by_date(start, end, krx_symbol)
        # pykrx already uses '시가', '고가', '저가', '종가', '거래량'
        return df

    def get_vix_history(self, start_date: str, end_date: str) -> pd.DataFrame:
        # pykrx doesn't directly support VIX
        return fdr.DataReader("^VIX", start=start_date, end=end_date)

    def get_etf_list(self) -> pd.DataFrame:
        # Use FDR for ETF listing as it's convenient
        etf_list = fdr.StockListing('ETF/KR')
        exclude_keywords = ['인버스', '레버리지', r'\(H\)']
        mask = ~etf_list['Name'].str.contains('|'.join(exclude_keywords), regex=True, na=False)
        filtered_etf = etf_list[mask]
        filtered_etf = filtered_etf.sort_values('Volume', ascending=False)
        return filtered_etf
