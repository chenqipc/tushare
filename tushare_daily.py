import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from tushare_token import tushare_token


def get_daily():
    # 初始化pro接口
    pro = ts.pro_api(tushare_token)

    # 读取存储的股票数据
    stock_data = pd.read_json('stock_data.json')

    # 获取当前日期
    today = datetime.today()
    # 计算一个月前的日期
    one_month_ago = today - timedelta(days=30)
    start_date = one_month_ago.strftime('%Y%m%d')
    end_date = today.strftime('%Y%m%d')

    # 遍历每支股票
    for index, row in stock_data.iterrows():
        ts_code = row['ts_code']
        name = row['name']

        # 获取近一个月内的每日涨跌情况和交易量
        daily_data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

        if not daily_data.empty:
            # 输出该股票的涨跌幅和成交量
            print(f"股票代码: {ts_code}, 名称: {name}")
            print(daily_data[['trade_date', 'close', 'pct_chg', 'vol']])
        else:
            print(f"股票代码: {ts_code}, 名称: {name}在最近一个月内无数据")
