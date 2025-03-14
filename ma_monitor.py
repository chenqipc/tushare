import pandas as pd
from datetime import datetime, timedelta
from eastmoney_crawler import EastMoneyAPI
from gui_utils import NotificationManager
from log_utils import LoggerManager

# 初始化东方财富API
api = EastMoneyAPI()
notify = NotificationManager()

def get_ma_data(ts_code, period='D', start_date=None, end_date=None, ts_name=None):
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
        ts_name: ETF中文名称
    """
    # 如果没有提供中文名称，使用代码作为名称
    if ts_name is None:
        ts_name = ts_code
        
    # 使用日志工具类获取日志记录器
    logger = LoggerManager.get_logger(f"{ts_code}_{ts_name}")
    
    if start_date is None:
        start_date = (datetime.today() - timedelta(days=120)).strftime('%Y%m%d')
    if end_date is None:
        end_date = datetime.today().strftime('%Y%m%d')
    
    # 提取纯代码（去掉可能的后缀如.SZ）
    symbol = ts_code.split('.')[0]
        
    try:
        if period == 'D':
            df = api.get_daily_data(symbol, start_date, end_date)
        elif period == '120min':
            # 调用合并60分钟数据的函数
            df = api.merge_60min_to_120min(symbol, start_date, end_date)
        else:
            df = api.get_minute_data(symbol, period, start_date, end_date)
            
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
        logger.error(f"获取数据失败：{str(e)}")
        return None


def check_ma_cross(df, ts_code=None, period_name=None, ts_name=None):
    """
    检查是否上穿三条均线
    返回：
        - True: 当前价格在三条均线上方
        - False: 当前价格未在三条均线上方
    
    参数：
        df: 数据框
        ts_code: 股票或ETF代码
        period_name: 周期名称
        ts_name: 股票或ETF中文名称
    """
    if df is None or df.empty or len(df) < 2:
        return False
    
    # 如果没有提供中文名称，使用代码作为名称
    if ts_name is None:
        ts_name = ts_code
    
    # 使用日志工具类获取日志记录器
    logger = LoggerManager.get_logger(f"{ts_code}_{ts_name}") if ts_code else None
        
    # 获取最新一条和前一条数据
    latest = df.iloc[-1]
    previous = df.iloc[-2]
    
    # 检查当前价格是否在三条均线上方
    price = latest['close']
    ma10 = latest['MA10']
    ma30 = latest['MA30']
    ma60 = latest['MA60']
    
    # 获取前一个周期的价格（但使用当前周期的均线数据）
    prev_price = previous['close']
    
    # 判断是否存在空值
    if pd.isna(ma10) or pd.isna(ma30) or pd.isna(ma60):
        return False
    
    # 只有当提供了代码和周期名称时才记录详细信息
    if ts_code and period_name and logger:
        # 判断是否上穿10日均线或下穿10日均线
        if price > ma10:
            if prev_price <= ma10:
                message = f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格上穿了10日均线"
                notify.show_notification(f"{ts_code} ({ts_name})", message, 5)
                logger.info(message)
            else:
                logger.info(f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格持续在10日均线上方")
        else:
            if prev_price >= ma10:
                message = f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格下穿了10日均线"
                notify.show_notification(f"{ts_code} ({ts_name})", message, 5)
                logger.info(message)
            else:
                logger.info(f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格持续在10日均线下方")
                
        # 判断是否上穿30日均线或下穿30日均线
        if price > ma30:
            if prev_price <= ma30:
                message = f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格上穿了30日均线"
                notify.show_notification(f"{ts_code} ({ts_name})", message, 5)
                logger.info(message)
            else:
                logger.info(f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格持续在30日均线上方")
        else:
            if prev_price >= ma30:
                message = f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格下穿了30日均线"
                notify.show_notification(f"{ts_code} ({ts_name})", message, 5)
                logger.info(message)
            else:
                logger.info(f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格持续在30日均线下方")
                
        # 判断是否上穿60日均线或下穿60日均线
        if price > ma60:
            if prev_price <= ma60:
                message = f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格上穿了60日均线"
                notify.show_notification(f"{ts_code} ({ts_name})", message, 5)
                logger.info(message)
            else:
                logger.info(f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格持续在60日均线上方")
        else:
            if prev_price >= ma60:
                message = f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格下穿了60日均线"
                notify.show_notification(f"{ts_code} ({ts_name})", message, 5)
                logger.info(message)
            else:
                logger.info(f"{ts_code} ({ts_name}) 在 {period_name} 周期当前价格持续在60日均线下方")

    # 判断价格是否在三条均线上方
    return price > ma10 and price > ma30 and price > ma60


def monitor_etf(ts_code, period='D', ts_name=None):
    """
    监控ETF在指定周期的均线状态
    
    参数：
        ts_code: ETF代码
        period: 周期，支持 1min/5min/15min/30min/60min/D
        ts_name: ETF中文名称
    """
    # 如果没有提供中文名称，使用代码作为名称
    if ts_name is None:
        ts_name = ts_code
        
    # 使用日志工具类获取日志记录器
    logger = LoggerManager.get_logger(f"{ts_code}_{ts_name}")
    
    df = get_ma_data(ts_code, period)
    if df is not None:
        period_name = '日线' if period == 'D' else f'{period}线'
        is_above_ma = check_ma_cross(df, ts_code, period_name, ts_name)
        return is_above_ma
    return False
