import yfinance as yf
import pandas as pd
import numpy as np
import os

def create_folders():
    folders = ['raw_data', 'kline_data', 'feature_data', 'final_data']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

def fetch_stock_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        file_path = f"raw_data/{ticker}_data.csv"
        if not os.path.exists(file_path):
            print(f"正在下載 {ticker} 的交易資料...")
            df = yf.download(ticker, start=start_date, end=end_date)
            df.to_csv(file_path)
            
    return data

def calculate_kline_features(df):
    # 計算上影線、下影線、實體線的長度(%)
    df['Upper_Shadow'] = (df['High'] - np.maximum(df['Open'], df['Close'])) / df['Close'] * 100
    df['Lower_Shadow'] = (np.minimum(df['Open'], df['Close']) - df['Low']) / df['Close'] * 100
    df['Body_Length'] = (df['Close'] - df['Open']) / df['Close'] * 100

    # 前一日上影線、下影線、實體線
    df['Prev_Upper_Shadow'] = df['Upper_Shadow'].shift(1)
    df['Prev_Lower_Shadow'] = df['Lower_Shadow'].shift(1)
    df['Prev_Body_Length'] = df['Body_Length'].shift(1)

    # 開盤型態、收盤型態
    df['Opening_Type'] = (df['Open'] - df['Close'].shift(1)) / df['Close'] * 100
    df['Closing_Type'] = (df['Close'] - df['Close'].shift(1)) / df['Close'] * 100

    # 當日成交量與5日均量二者之差的比率
    df['5Day_MA_Volume'] = df['Volume'].rolling(window=5).mean()
    df['Volume_Ratio'] = (df['Volume'] - df['5Day_MA_Volume']) / df['Volume']

    # 前五日趨勢
    df['5Day_Trend'] = (df['Close'].shift(2) - df['Close'].shift(7)) / df['Close'].shift(7)

    return df

def process_csv_files(tickers):
    kline_data = {}
    for ticker in tickers:
        print(f"正在處理 {ticker} 的K線數據...")
        try:
            df = pd.read_csv(f"raw_data/{ticker}_data.csv", skiprows=2)
            df.columns = ["Date", "Adj Close","Close", "High", "Low", "Open", "Volume"]
            df.set_index("Date", inplace=True)
            df.index = pd.to_datetime(df.index)
            kline_data[ticker] = calculate_kline_features(df)
            df.to_csv(f"kline_data/{ticker}_KlineData.csv")
            print(f"{ticker} 的K線特徵已保存。")
        except Exception as e:
            print(f"無法處理 {ticker} 的數據: {e}")
    return kline_data

def calculate_future_returns(df, periods=[3, 20, 60]):
    for period in periods:
        df[f'Return_{period}d'] = (df['Close'].shift(-period) - df['Close']) / df['Close']
    return df

def process_future_returns(tickers):
    for ticker in tickers:
        try:
            df = pd.read_csv(f"kline_data/{ticker}_KlineData.csv", index_col='Date')
            df.index = pd.to_datetime(df.index)
            df = calculate_future_returns(df)
            df.to_csv(f"feature_data/{ticker}_FeatureData.csv")
            print(f"{ticker} 的收益數據已保存。")
        except Exception as e:
            print(f"處理 {ticker} 時出錯: {e}")

def mark_significant_changes(df, threshold=0.05):
    df['Significant_Rise_3d'] = df['Return_3d'] > threshold
    df['Significant_Drop_3d'] = df['Return_3d'] < -threshold
    df['Significant_Rise_20d'] = df['Return_20d'] > threshold
    df['Significant_Drop_20d'] = df['Return_20d'] < -threshold
    df['Significant_Rise_60d'] = df['Return_60d'] > threshold
    df['Significant_Drop_60d'] = df['Return_60d'] < -threshold
    return df

def process_significant_changes(tickers):
    for ticker in tickers:
        try:
            df = pd.read_csv(f"feature_data/{ticker}_FeatureData.csv", index_col='Date')
            df.index = pd.to_datetime(df.index)
            df = mark_significant_changes(df)
            df.to_csv(f"final_data/{ticker}_Final_FeatureData.csv")
            print(f"{ticker} 的大漲/大跌標記已完成並保存。")
        except Exception as e:
            print(f"處理 {ticker} 時出錯: {e}")

if __name__ == "__main__":
    tickers = [
    "2330.TW",  # 台積電
    "3041.TW",  # 楊智
    "2481.TW",  # 強茂
    "2342.TW",  # 茂矽
    "2302.TW",  # 麗正
    "2303.TW",  # 聯電
    "2329.TW",  # 華泰
    "3545.TW",  # 敦泰
    "6525.TW",  # 捷敏-KY
    "2451.TW"   # 創見
    ]
    start_date = "2015-01-01"
    end_date = "2023-12-31"

    create_folders()
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    kline_data = process_csv_files(tickers)
    process_future_returns(tickers)
    process_significant_changes(tickers)