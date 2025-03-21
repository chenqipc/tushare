import time
import pandas as pd
import StockEnum
from tushare_check import daily_check
import os


def traversal():
    file_dict = {}
    for stock_status in StockEnum.StockStatus:
        file_name = f"{stock_status.value}.txt"
        f = open(file_name, 'w')
        file_dict[stock_status] = f

    # 读取存储的股票数据
    stock_data = pd.read_json('stock_data.json')

    for index, row in stock_data.iterrows():
        if not isinstance(index, int):
            print("不是int类型")
            break
        if isinstance(index, int) and index < 0:
            continue

        ts_code = row['ts_code']
        name = row['name']
        print("[%s][%s]" % (ts_code, name))

        # 调用 daily_check 函数获取结果
        res = daily_check(ts_code, name)

        if StockEnum.StockStatus.NO_MATCH in res:
            print(f"[{ts_code}][{name}]不符合要求")
        if StockEnum.StockStatus.THREE_LIMIT_UP in res:
            print(f"[{ts_code}][{name}] 连续3天涨停")
            file_dict[StockEnum.StockStatus.THREE_LIMIT_UP].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.THREE_LIMIT_UP_ONLY in res:
            print(f"[{ts_code}][{name}] 最近3天涨停")
            file_dict[StockEnum.StockStatus.THREE_LIMIT_UP_ONLY].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.RISING_VOLUME_INCREASE in res:
            print(f"[{ts_code}][{name}] 连续5天上涨且成交量增加")
            file_dict[StockEnum.StockStatus.RISING_VOLUME_INCREASE].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.VOLUME_SURGE_WITH_PRICE_RISE in res:
            print(f"[{ts_code}][{name}] 出现大幅放量伴随上涨")
            file_dict[StockEnum.StockStatus.VOLUME_SURGE_WITH_PRICE_RISE].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.CAPITAL_INFLOW in res:
            print(f"[{ts_code}][{name}] 出现资金流入明显")
            file_dict[StockEnum.StockStatus.CAPITAL_INFLOW].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.SUPPORT_LEVEL_REBOUND in res:
            print(f"[{ts_code}][{name}] 出现底部支撑反弹")
            file_dict[StockEnum.StockStatus.SUPPORT_LEVEL_REBOUND].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.MACD_GOLDEN_CROSS in res:
            print(f"[{ts_code}][{name}] 出现MACD金叉")
            file_dict[StockEnum.StockStatus.MACD_GOLDEN_CROSS].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.DOUBLE_BOTTOM in res:
            print(f"[{ts_code}][{name}] 出现双底结构")
            file_dict[StockEnum.StockStatus.DOUBLE_BOTTOM].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.BREAKOUT_AFTER_CONSOLIDATION in res:
            print(f"[{ts_code}][{name}] 横盘后放量上涨")
            file_dict[StockEnum.StockStatus.BREAKOUT_AFTER_CONSOLIDATION].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.IS_UPWARD_TREND in res:
            print(f"[{ts_code}][{name}] 处于上涨初期")
            file_dict[StockEnum.StockStatus.IS_UPWARD_TREND].write(f"{ts_code} {name}\n")
        if StockEnum.StockStatus.MACD_GOLDEN_CROSS_OVER_7 in res:
            print(f"[{ts_code}][{name}] 最近7天MACD金叉")
            file_dict[StockEnum.StockStatus.MACD_GOLDEN_CROSS_OVER_7].write(f"{ts_code} {name}\n")

        # 延迟3秒
        time.sleep(1)

    # 现在关闭字典中所有的文件对象
    for file_obj in file_dict.values():
        file_obj.close()

    for stock_status in StockEnum.StockStatus:
        file_name = f"{stock_status.value}.txt"
        remove_empty_file(file_name)


def remove_empty_file(file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 打开文件，检查内容是否为空
        with open(file_path, 'r') as file:
            content = file.read().strip()  # 去除空白字符
        # 如果内容为空，则删除文件
        if not content:
            os.remove(file_path)
            print(f"已删除空文件: {file_path}")
        else:
            print(f"文件不是空的: {file_path}")
    else:
        print(f"文件不存在: {file_path}")


if __name__ == '__main__':
    traversal()
