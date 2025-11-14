from vnstock import Quote
from vnstock import Company
from datetime import datetime, timedelta
from typing import List, Optional
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import json

quote = Quote(symbol='VCI', source='VCI')
company = Company(symbol='VCB', source='TCBS')

def get_shareholders(ticker: str):
    company = Company(symbol=ticker, source='TCBS')
    data = company.shareholders()
    return data
def get_officers(ticker, filter_by="working"):
   
    company = Company(symbol=ticker, source='TCBS')
    data = company.officers(filter_by=filter_by)
    return data
def get_subsidiaries(ticker):
    from vnstock import Company
    company = Company(symbol=ticker, source='TCBS')
    data = company.subsidiaries()
    return data



def get_historical_price(ticker, start_date=None, end_date=None, time_range=None, month=None, resolution="1d", sma_window=None, rsi_window=None):
    
    if isinstance(ticker, str):
        tickers = [ticker]
    else:
        tickers = ticker

    today = datetime.today()

    # Tính start/end nếu time_range
    if time_range:
        unit = time_range[-1]
        value = int(time_range[:-1])
        if unit == "d":
            start_date = today - timedelta(days=value)
        elif unit == "w":
            start_date = today - timedelta(weeks=value)
        elif unit == "m":
            start_date = today - relativedelta(months=value)
        elif time_range == "ytd":
            start_date = datetime(today.year, 1, 1)
        end_date = today

    # Tính start/end nếu month
    elif month:
        year = today.year
        if month > datetime.now().month:
            year -= 1
        start_date = datetime(year, month, 1)
        last_day = monthrange(year, month)[1]
        end_date = today

    # Nếu start_date/end_date là string
    elif start_date and end_date:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")



    result = {}
    for sym in tickers:
        quote = Quote(symbol=sym, source="TCBS")
        df = quote.history(start=start_str, end=end_str)

        
        if not df.empty:
            if sma_window:
                for window in sma_window:
                    df[f'SMA_{window}'] = df['close'].rolling(window=window).mean().round(2)
            
            if rsi_window:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=rsi_window).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=rsi_window).mean()
                rs = gain / loss
                df[f'RSI_{rsi_window}'] = (100 - (100 / (1 + rs))).round(2)
        
        result[sym] = df.to_dict(orient='records')

    return result

if __name__ == "__main__":
    # 1. Danh sách cổ đông VCB
    shareholders = get_shareholders("VCB")
    print("Cổ đông VCB:", shareholders)
    # 2. Lãnh đạo đang làm việc VCB
    officers = get_officers("VCB")
    print("Lãnh đạo VCB:", officers)
    # 3. Công ty con VCB
    subs = get_subsidiaries("VCB")
    print("Công ty con VCB:", subs)
    # 4. So sánh VIC & HPG 2 tuần gần đây
    data = get_historical_price(["VIC","HPG"], time_range="2w")
    print("Giá VIC & HPG 2 tuần:", data)
    # 5. Giá đóng VCB từ đầu tháng 11
    data_vcb = get_historical_price("VCB", month=11)
    print("Giá VCB tháng 11:", data_vcb)
    # 6. Giá từ 2023-10-01 đến 2023-10-31 HPG
    data_hpg = get_historical_price("HPG", start_date="2023-10-01", end_date="2023-10-31")
    print("Giá HPG 10/2023:", data_hpg)
