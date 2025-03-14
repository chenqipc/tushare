import pandas as pd
from datetime import datetime, timedelta
import time
import schedule
from eastmoney_crawler import EastMoneyAPI
from ma_monitor import get_ma_data, check_ma_cross

# 初始化东方财富API
api = EastMoneyAPI()

def monitor_symbol(symbol_code, periods=['15min', '30min', '60min', '120min']):
    """
    监控指定股票或ETF在多个周期的均线状态
    
    参数：
        symbol_code: 股票或ETF代码
        periods: 要监控的周期列表
    """
    print(f"\n========== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 开始监控 {symbol_code} ==========")
    
    # 先测试市场识别
    market_id, full_symbol = api.get_market_id(symbol_code, 'ETF')
    print(f"市场信息：市场代码={market_id}, 完整代码={full_symbol}")

    if not market_id:
        print(f"无法识别代码 {symbol_code} 的市场信息，请检查代码是否正确")
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


def start_monitoring(symbol_code, interval_minutes=15):
    """
    开始定时监控
    
    参数：
        symbol_code: 要监控的股票或ETF代码
        interval_minutes: 监控间隔（分钟）
    """
    print(f"开始监控 {symbol_code}，每 {interval_minutes} 分钟检查一次")
    
    # 立即执行一次
    monitor_symbol(symbol_code)
    
    # 设置定时任务
    schedule.every(interval_minutes).minutes.do(monitor_symbol, symbol_code=symbol_code)
    
    # 运行定时任务
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("监控已停止")


if __name__ == '__main__':
    # 设置要监控的股票或ETF代码
    symbol_to_monitor = '512980'  # 传媒ETF
    
    # 开始定时监控，每15分钟检查一次
    start_monitoring(symbol_to_monitor, 15)