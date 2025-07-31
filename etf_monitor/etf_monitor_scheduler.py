import time
from datetime import datetime, timedelta

import schedule

from eastmoney_crawler import EastMoneyAPI
from common.log_utils import LoggerManager
from ma_monitor import get_ma_data, check_ma_cross

# 初始化东方财富API
api = EastMoneyAPI()

def monitor_symbol(symbol_code, symbol_name=None, period=None):
    """
    监控指定股票或ETF在指定周期的均线状态
    
    参数：
        symbol_code: 股票或ETF代码
        symbol_name: 股票或ETF中文名称
        period: 要监控的周期，如 '15min', '30min', '60min', '120min'
    """
    # 如果没有提供中文名称，使用代码作为名称
    if symbol_name is None:
        symbol_name = symbol_code
    
    # 获取该股票的日志记录器
    logger = LoggerManager.get_logger(f"{symbol_code}_{symbol_name}")
    
    # 如果没有指定周期，则默认监控所有周期
    periods = [period] if period else ['15min', '30min', '60min', '120min']
    
    logger.info(f"\n========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始监控 {symbol_code} ({symbol_name}) {period if period else '所有周期'} ==========")
    
    # 先测试市场识别
    market_id, full_symbol = api.get_market_id(symbol_code, 'ETF')
    logger.info(f"市场信息：市场代码={market_id}, 完整代码={full_symbol}")

    if not market_id:
        logger.warning(f"无法识别代码 {symbol_code} 的市场信息，请检查代码是否正确")
        return

    # 计算三个月前的日期
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y%m%d')
    end_date = datetime.today().strftime('%Y%m%d')
    logger.info(f"获取从 {start_date} 到 {end_date} 的数据")
    
    # 监控指定周期
    for p in periods:
        logger.info(f"\n----- {p} 周期分析 -----")
        df = get_ma_data(symbol_code, p, start_date, end_date, symbol_name)
        if df is not None:
            # 记录数据量
            logger.info(f"获取到 {len(df)} 条数据")
            # 检查均线状态
            period_name = f'{p}线'
            is_above_ma = check_ma_cross(df, symbol_code, period_name, symbol_name)
            status = '上方' if is_above_ma else '下方'
            logger.info(f"{symbol_code} ({symbol_name}) 在 {period_name} 周期当前价格位于三条均线{status}")
        else:
            logger.warning(f"无法获取 {symbol_code} ({symbol_name}) 的 {p} 周期数据")
    
    logger.info(f"========== 监控完成 ==========\n")


def setup_monitoring_tasks(symbols_to_monitor):
    """
    为多个股票或ETF设置按照不同周期错开的监控任务
    参数：
        symbols_to_monitor: 要监控的股票或ETF代码列表格式为 [代码, 中文名称]
    """

    # 获取主日志记录器
    main_logger = LoggerManager.get_logger('main')
    
    # 定义不同周期的监控间隔（分钟）
    periods = {
        '15min': 15,
        '30min': 30,
        '60min': 60,
        '120min': 120
    }
    
    # 为每个股票和每个周期设置错开的定时任务
    for i, symbol_info in enumerate(symbols_to_monitor):
        # 解析代码和名称
        if isinstance(symbol_info, list) and len(symbol_info) >= 2:
            symbol_code = symbol_info[0]
            symbol_name = symbol_info[1]
        else:
            # 兼容旧格式
            symbol_code = symbol_info
            symbol_name = symbol_info
        
        # 为每个周期设置单独的调度任务
        for period, interval_minutes in periods.items():
            # 为每个股票和周期组合生成唯一的偏移时间
            # 基础偏移为股票索引（确保不同股票错开）
            base_offset = i % interval_minutes
            
            # 设置定时任务，使用错开的时间
            schedule.every(interval_minutes).minutes.at(f":{base_offset:02d}").do(
                scheduled_monitor, 
                symbol_code=symbol_code, 
                symbol_name=symbol_name,
                period=period
            )
            main_logger.info(f"已设置 {symbol_code} ({symbol_name}) 的 {period} 周期监控任务，每{interval_minutes}分钟执行一次，偏移{base_offset}分钟")
        
        # 立即执行第一个股票的所有周期监控（如果当前是交易时间）
        if i == 0 and is_trading_time():
            main_logger.info(f"立即开始监控 {symbol_code} ({symbol_name}) 的所有周期")
            monitor_symbol(symbol_code, symbol_name=symbol_name)
    
    main_logger.info("所有监控任务已设置，开始运行调度器...")


def scheduled_monitor(symbol_code, symbol_name=None, period=None):
    """
    定时任务调用的监控函数，会先检查是否是交易时间
    
    参数：
        symbol_code: 股票或ETF代码
        symbol_name: 股票或ETF中文名称
        period: 要监控的周期
    """
    # 获取主日志记录器
    main_logger = LoggerManager.get_logger('main')
    
    # 检查是否是交易时间
    if not is_trading_time():
        main_logger.info(f"当前不是交易时间，跳过 {symbol_code} ({symbol_name}) 的 {period} 周期监控")
        return
    
    # 是交易时间，执行监控
    monitor_symbol(symbol_code, symbol_name=symbol_name, period=period)


def is_trading_time():
    """
    判断当前是否是A股交易时间
    
    返回：
        - True: 当前是交易时间（工作日9:00-15:00）
        - False: 当前不是交易时间
    """
    now = datetime.now()
    
    # 检查是否是周末（5是周六，6是周日）
    if now.weekday() >= 5:
        return False
    
    # 检查是否在交易时间内（9:00-15:00）
    trading_start = datetime(now.year, now.month, now.day, 9, 0, 0)
    trading_end = datetime(now.year, now.month, now.day, 15, 0, 0)
    
    return trading_start <= now <= trading_end


def start_scheduler():
    """
    启动调度器，运行所有已设置的监控任务
    """
    # 获取主日志记录器
    main_logger = LoggerManager.get_logger('main')
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        main_logger.info("所有监控已停止")


if __name__ == '__main__':
    # 设置要监控的股票或ETF代码列表，格式为 [代码, 中文名称]
    symbols_to_monitor = [
        ['515220', '煤炭ETF'],
        ['512980', '传媒ETF'],
        ['515050', '5GETF'],
        ['562500', '机器人ETF'],
        ['512930', '人工智能ETF'],
        # ['512880', '证券ETF'],
        # ['512480', '半导体ETF'],
        ['516010', '游戏ETF']
    ]
    
    # 设置监控任务
    setup_monitoring_tasks(symbols_to_monitor)
    
    # 启动调度器
    start_scheduler()