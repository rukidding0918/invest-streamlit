import FinanceDataReader as fdr
import pandas as pd

def get_top_etfs(n: int = 20) -> pd.DataFrame:
    """
    Fetch and filter Korean ETFs, returning the top N by volume.
    Excludes Inverse, Leverage, and Hedged (H) ETFs.
    """
    etf_list = fdr.StockListing('ETF/KR')

    # 제외 키워드
    exclude_keywords = ['인버스', '레버리지', r'\(H\)']

    # 필터링 (regex=True 명시, 괄호 이스케이프)
    mask = ~etf_list['Name'].str.contains('|'.join(exclude_keywords), regex=True, na=False)
    filtered_etf = etf_list[mask]

    # Volume 정렬 및 상위 N개 추출
    top_etfs = filtered_etf.sort_values('Volume', ascending=False).head(n)
    
    return top_etfs
