from abc import ABC, abstractmethod
import pandas as pd

class DataLoader(ABC):
    @abstractmethod
    def get_index_ohlcv(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch index OHLCV data and follow a standard column naming convention.
        Standard columns: ['시가', '고가', '저가', '종가', '거래량']
        Dates format: YYYYMMDD or YYYY-MM-DD (provider dependent, but we'll try to normalize)
        """
        pass

    @abstractmethod
    def get_vix_history(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch VIX index history."""
        pass
