import pandas as pd
from datetime import datetime, timedelta
import time
import schedule
from eastmoney_crawler import EastMoneyAPI
from ma_monitor import get_ma_data, check_ma_cross
from log_utils import LoggerManager

# 初始化东方财富API
api = EastMoneyAPI()

def monitor_symbol(symbol_code, periods=['15min', '30min', '60min', '120min']):
    """
    监控指定股票或ETF在多个周期的均线状态
    
    参数：
        symbol_code: 股票或ETF代码
        periods: 要监控的周期列表
    """
    # 获取该股票的日志记录器
    logger = LoggerManager.get_logger(symbol_code)
    
    logger.info(f"\n========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始监控 {symbol_code} ==========")
    
    # 先测试市场识别
    market_id, full_symbol = api.get_market_id(symbol_code, 'ETF')
    logger.info(f"市场信息：市场代码={market_id}, 完整代码={full_symbol}")

    if not market_id:
        logger.warning(f"无法识别代码 {symbol_code} 的市场信息，请检查代码是否正确")
        return

    # 计算三个月前的日期
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y%m%d')
    end_date = datetime.today().strftime('%Y%m%d')
    print(f"获取从 {start_date} 到 {end_date} 的数据")
    
    # 监控不同周期
    for period in periods:
        print(f"\n----- {period} 周期分析 -----")
        df = get_ma_data(symbol_code, period, start_date, end_date)
        if df is not None:
            # 打印数据量
            print(f"获取到 {len(df)} 条数据")
            # 检查均线状态
            period_name = f'{period}线'
            is_above_ma = check_ma_cross(df, symbol_code, period_name)
            status = '上方' if is_above_ma else '下方'
            print(f"{symbol_code} 在 {period_name} 周期当前价格位于三条均线{status}")
        else:
            print(f"无法获取 {symbol_code} 的 {period} 周期数据")
    
    print(f"========== 监控完成 ==========\n")


def setup_monitoring_tasks(symbols_to_monitor, interval_minutes=15):
    """
    为多个股票或ETF设置错开的监控任务
    
    参数：
        symbols_to_monitor: 要监控的股票或ETF代码列表
        interval_minutes: 监控间隔（分钟），默认15分钟
    """
    import random
    
    # 获取主日志记录器
    main_logger = LoggerManager.get_logger('main')
    
    # 创建一个已使用的偏移时间集合，用于确保偏移时间的唯一性
    used_offsets = set()
    
    # 为每个股票设置错开的定时任务
    for i, symbol in enumerate(symbols_to_monitor):
        # 生成唯一的偏移时间（分钟）
        while True:
            # 基础偏移为股票索引乘以最小间隔（确保至少相差1分钟）
            base_offset = i * 1
            # 添加一些随机性（0-2分钟）
            random_offset = random.randint(0, 2)
            offset_minutes = base_offset + random_offset
            
            # 确保偏移时间在合理范围内（小于监控间隔）
            offset_minutes = offset_minutes % interval_minutes
            
            # 检查是否已使用过这个偏移时间
            if offset_minutes not in used_offsets:
                used_offsets.add(offset_minutes)
                break
        
        # 立即执行第一个股票的监控
        if i == 0:
            main_logger.info(f"立即开始监控 {symbol}")
            monitor_symbol(symbol)
        
        # 设置定时任务，使用错开的时间
        schedule.every(interval_minutes).minutes.at(f":{offset_minutes:02d}").do(monitor_symbol, symbol_code=symbol)
        main_logger.info(f"已设置 {symbol} 的监控任务，每{interval_minutes}分钟执行一次，偏移{offset_minutes}分钟")
    
    main_logger.info("所有监控任务已设置，开始运行调度器...")


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
    # 设置要监控的股票或ETF代码列表
    symbols_to_monitor = [
        '512980',  # 传媒ETF
        '515050',  # 5GETF
        '562550',  # 机器人
        '512930',  # 人工智能
        '512880',  # 证券ETF
        '512480'   # 半导体ETF
    ]
    
    # 设置监控任务
    setup_monitoring_tasks(symbols_to_monitor)
    
    # 启动调度器
    start_scheduler()