from datetime import date, timedelta

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from data_loader import get_loader, get_top_etfs

st.set_page_config(page_title="Invest Streamlit", layout="wide")

st.sidebar.title("Settings")
data_source = st.sidebar.selectbox("Data Source", ["fdr", "pykrx"], index=0)
loader = get_loader(data_source)

# Common settings
st.sidebar.markdown("---")
available_indices = ["KOSPI", "KOSDAQ", "S&P 500", "NASDAQ", "Dow Jones", "Nikkei 225"]
selected_index = st.sidebar.selectbox("Select Index", available_indices, index=0)

st.sidebar.subheader("Additional Indicators")
show_vix = st.sidebar.checkbox("Show VIX Index", value=False)

# Date Range Picker
today = date.today()
default_start = today - timedelta(days=365)
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(default_start, today),
    max_value=today
)

# Handle date range selection
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = default_start, today

tab1, tab2 = st.tabs(["Index Analysis", "Top 20 ETFs"])

with tab1:
    # Fetch index data
    try:
        df = loader.get_index_ohlcv(selected_index, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
    except Exception as e:
        st.error(f"Error fetching {selected_index} from {data_source}: {e}")
        df = None

    if df is not None and not df.empty:
        window = 20
        df['MA20'] = df['종가'].rolling(window=window).mean()
        df['std'] = df['종가'].rolling(window=window).std()
    
        # Bollinger Bands calculation
        for i in [1, 2, 3]:
            df[f'Upper{i}'] = df['MA20'] + (df['std'] * i)
            df[f'Lower{i}'] = df['MA20'] - (df['std'] * i)

        # Fetch VIX if requested
        vix_df = None
        if show_vix:
            try:
                vix_df = loader.get_vix_history(start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d"))
                if not vix_df.empty:
                    # Align VIX data to KOSPI dates (ffill for missing dates like holidays)
                    vix_df = vix_df[['Close']].reindex(df.index).ffill().bfill()
            except Exception as e:
                st.warning(f"Could not fetch VIX data: {e}")

        # Determine subplot rows
        num_rows = 3 if show_vix and vix_df is not None and not vix_df.empty else 2
        row_heights = [0.5, 0.25, 0.25] if num_rows == 3 else [0.7, 0.3]
        subplot_titles = (selected_index, "Volume", "VIX Index") if num_rows == 3 else (selected_index, "Volume")

        fig = make_subplots(rows=num_rows, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, 
                            row_heights=row_heights,
                            subplot_titles=subplot_titles)

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=df.index.strftime("%Y-%m-%d"),
            open=df['시가'], high=df['고가'],
            low=df['저가'], close=df['종가'],
            name=selected_index
        ), row=1, col=1)

        # Bollinger Bands Visualization (Shaded)
        # Order: 3std -> 2std -> 1std (stacking from outside in)
        band_colors = {
            1: 'rgba(100, 149, 237, 0.3)', # Deepest (inner)
            2: 'rgba(100, 149, 237, 0.2)', 
            3: 'rgba(100, 149, 237, 0.1)'  # Lightest (outer)
        }
        
        # Trace for shaded regions using 'fill'
        # We iterate backwards to ensure inner bands are filled on top or combined
        for i in [3, 2, 1]:
            # Upper line (anchor)
            fig.add_trace(go.Scatter(
                x=df.index.strftime("%Y-%m-%d"), y=df[f'Upper{i}'],
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ), row=1, col=1)
            
            # Lower line with fill to Upper line
            fig.add_trace(go.Scatter(
                x=df.index.strftime("%Y-%m-%d"), y=df[f'Lower{i}'],
                line=dict(width=0),
                fill='tonexty',
                fillcolor=band_colors[i],
                name=f'Bollinger {i}std',
                hoverinfo='skip'
            ), row=1, col=1)

        # MA20 line on top of fills
        fig.add_trace(go.Scatter(
            x=df.index.strftime("%Y-%m-%d"), y=df['MA20'],
            line=dict(color='orange', width=2),
            name='MA20'
        ), row=1, col=1)

        # Volume
        fig.add_trace(go.Bar(
            x=df.index.strftime("%Y-%m-%d"),
            y=df['거래량'],
            name="Volume",
            marker_color='blue'
        ), row=2, col=1)

        # VIX Index
        if num_rows == 3:
            fig.add_trace(go.Scatter(
                x=df.index.strftime("%Y-%m-%d"), # Use KOSPI index to align with category axis
                y=vix_df['Close'],
                name="VIX",
                line=dict(color='red', width=2)
            ), row=3, col=1)

        # Remove date gaps (including holidays) by treating x-axis as category
        for r in range(1, num_rows + 1):
            fig.update_xaxes(type='category', tickangle=-45, row=r, col=1)
        
        fig.update_layout(
            xaxis_rangeslider_visible=True, # Enable the range slider back
            height=900, # Increased height to accommodate the slider
            margin=dict(t=50, b=50, l=50, r=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, width="stretch")

        with st.expander("DataFrame"):
            st.dataframe(df.tail(10))

    else:
        st.error("No data available for the specified date range.")

with tab2:
    st.header("Top 20 ETFs by Volume")
    st.info("Korean ETFs excluding Inverse, Leverage, and Hedged products.")
    try:
        top_etfs = get_top_etfs(20)
        st.dataframe(top_etfs, width="stretch")
    except Exception as e:
        st.error(f"Error fetching ETF data: {e}")
