import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from tushare_token import tushare_token

# 初始化pro接口
pro = ts.pro_api(tushare_token)

def get_ma_data(ts_code, period='D', start_date=None, end_date=None):
    """
    获取ETF在指定周期的数据并计算移动平均线
    
    参数：
        ts_code: ETF代码
        period: 周期，支持：
            - 1min/5min/15min/30min/60min - 分钟
            - 120min - 2小时（由60分钟数据合并得到）
            - D - 日线
        start_date: 开始日期
        end_date: 结束日期
    """
    if start_date is None:
        start_date = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
    if end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
        
    try:
        if period == 'D':
            df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        elif period == '120min':
            # 调用合并60分钟数据的函数
            df = merge_60min_to_120min(ts_code, start_date, end_date)
        else:
            df = pro.stk_mins(ts_code=ts_code, start_date=start_date, end_date=end_date, freq=period)
            
        if df is None or df.empty:
            return None
            
        # 按时间正序排列
        df = df.sort_values('trade_date' if period == 'D' else 'trade_time')
        
        # 计算移动平均线
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA30'] = df['close'].rolling(window=30).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        return df
    except Exception as e:
        print(f"获取数据失败：{str(e)}")
        return None

def check_ma_cross(df):
    """
    检查是否上穿三条均线
    返回：
        - True: 当前价格在三条均线上方
        - False: 当前价格未在三条均线上方
    """
    if df is None or df.empty:
        return False
        
    # 获取最新一条数据
    latest = df.iloc[-1]
    
    # 检查当前价格是否在三条均线上方
    price = latest['close']
    ma10 = latest['MA10']
    ma30 = latest['MA30']
    ma60 = latest['MA60']
    
    # 判断是否存在空值
    if pd.isna(ma10) or pd.isna(ma30) or pd.isna(ma60):
        return False
    
    # 判断价格是否在三条均线上方
    return price > ma10 and price > ma30 and price > ma60

def monitor_etf(ts_code, period='D'):
    """
    监控ETF在指定周期的均线状态
    
    参数：
        ts_code: ETF代码
        period: 周期，支持 1min/5min/15min/30min/60min/D
    """
    df = get_ma_data(ts_code, period)
    if df is not None:
        is_above_ma = check_ma_cross(df)
        period_name = '日线' if period == 'D' else f'{period}线'
        status = '上方' if is_above_ma else '下方'
        print(f"{ts_code} 在 {period_name} 周期当前价格位于三条均线{status}")
        return is_above_ma
    return False


def merge_60min_to_120min(ts_code, start_date, end_date):
    """
    将60分钟数据合并为120分钟数据
    
    参数：
        ts_code: ETF代码
        start_date: 开始日期
        end_date: 结束日期
    返回：
        合并后的120分钟数据DataFrame
    """
    # 获取60分钟数据然后合并
    df = pro.stk_mins(ts_code=ts_code, start_date=start_date, end_date=end_date, freq='60min')
    if df is not None and not df.empty:
        # 确保数据按时间排序
        df = df.sort_values('trade_time')
        # 每两个60分钟数据合并为一个120分钟数据
        df['group'] = df.index // 2
        df = df.groupby('group').agg({
            'trade_time': 'first',  # 取第一个时间
            'open': 'first',        # 取第一个开盘价
            'high': 'max',          # 取最高价
            'low': 'min',           # 取最低价
            'close': 'last',        # 取最后收盘价
            'vol': 'sum',           # 成交量相加
            'amount': 'sum'         # 成交额相加
        }).reset_index(drop=True)
    return df
    

# 使用示例
if __name__ == '__main__':
    etf_code = '159915.SZ'  # 创业板ETF
    
    # 监控不同周期
    periods = ['D', '120min', '60min', '15min', '1min']
    for period in periods:
        monitor_etf(etf_code, period)