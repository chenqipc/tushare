import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def merge_60min_to_120min(symbol):
    """
    将60分钟数据合并为120分钟数据
    """
    # 获取60分钟数据
    df = ak.stock_zh_a_minute(symbol=symbol, period='60')
    
    if df is not None and not df.empty:
        # 确保数据按时间排序
        df = df.sort_values('datetime')
        # 每两个60分钟数据合并为一个120分钟数据
        df['group'] = df.index // 2
        df = df.groupby('group').agg({
            'datetime': 'first',    # 取第一个时间
            'open': 'first',        # 取第一个开盘价
            'high': 'max',          # 取最高价
            'low': 'min',           # 取最低价
            'close': 'last',        # 取最后收盘价
            'volume': 'sum',        # 成交量相加
            'amount': 'sum'         # 成交额相加
        }).reset_index(drop=True)
    return df

def get_ma_data_ak(symbol, period='daily', start_date=None, end_date=None):
    """
    使用AKShare获取ETF在指定周期的数据并计算移动平均线
    
    参数：
        symbol: ETF代码（如：159915）
        period: 周期，支持：
            - 1/5/15/30/60/120 - 分钟
            - daily - 日线
        start_date: 开始日期
        end_date: 结束日期
    """
    try:
        if period == 'daily':
            # 获取日线数据
            df = ak.fund_etf_hist_em(symbol=symbol, period="daily", start_date=start_date, end_date=end_date)
        elif period == '120':
            # 获取120分钟数据（通过合并60分钟数据）
            df = merge_60min_to_120min(symbol)
        else:
            # 获取分钟级数据
            df = ak.stock_zh_a_minute(symbol=symbol, period=period)
            
        if df is None or df.empty:
            return None
            
        # 重命名列以匹配原代码
        df = df.rename(columns={
            'datetime': 'trade_time',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'vol',
            'amount': 'amount'
        })
        
        # 计算移动平均线
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA30'] = df['close'].rolling(window=30).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        return df
    except Exception as e:
        print(f"获取数据失败：{str(e)}")
        return None

def monitor_etf_ak(symbol, period='daily'):
    """
    使用AKShare监控ETF在指定周期的均线状态
    
    参数：
        symbol: ETF代码（如：159915）
        period: 周期，支持 1/5/15/30/60/daily
    """
    df = get_ma_data_ak(symbol, period)
    if df is not None:
        is_above_ma = check_ma_cross(df)
        period_name = '日线' if period == 'daily' else f'{period}分钟线'
        status = '上方' if is_above_ma else '下方'
        print(f"{symbol} 在 {period_name} 周期当前价格位于三条均线{status}")
        return is_above_ma
    return False

# 使用示例
if __name__ == '__main__':
    etf_code = '159915'  # 创业板ETF
    
    # 监控不同周期
    periods = ['daily', '120', '60', '15', '1']
    for period in periods:
        monitor_etf_ak(etf_code, period)