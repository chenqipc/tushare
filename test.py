import akshare as ak

# 获取所有 ETF 列表
etf_list = ak.fund_etf_category_em()

# 显示前 5 行数据
print(etf_list.head())

# 保存为 CSV 文件
etf_list.to_csv("etf_list.csv", index=False)