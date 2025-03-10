import tushare as ts
from tushare_token import tushare_token


def all_stock():
    # 初始化pro接口
    pro = ts.pro_api(tushare_token)

    # 拉取数据
    df = pro.stock_basic(
        **{"ts_code": "", "name": "", "exchange": "", "market": "", "is_hs": "", "list_status": "", "limit": "",
           "offset": ""},
        fields=["ts_code", "symbol", "name", "market", "list_date"])
    print(df)

    df.to_json('stock_data.json', orient='records', force_ascii=False)

    print("数据已保存到stock_data.json文件中。")


if __name__ == '__main__':
    all_stock()
