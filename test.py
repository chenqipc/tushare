# 导入tushare
import tushare as ts

# 初始化pro接口
pro = ts.pro_api('8f61b794e37d65325f31bbd7cd4bc4055996e79f30a6470308757166')

# 拉取数据
df = pro.stock_basic(
    **{"ts_code": "", "name": "", "exchange": "", "market": "", "is_hs": "", "list_status": "", "limit": "", "offset": ""},
    fields=["ts_code", "symbol", "name", "market", "list_date"])
print(df)

df.to_json('stock_data.json', orient='records', force_ascii=False)

print("数据已保存到stock_data.json文件中。")
