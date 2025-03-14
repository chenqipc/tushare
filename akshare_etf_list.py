import akshare as ak
import pandas as pd

def get_all_etfs():
    """
    获取A股市场所有ETF基金的基本信息
    返回：包含ETF基本信息的DataFrame
    """
    try:
        # 使用 fund_etf_spot_em 接口获取ETF基金列表
        etf_df = ak.fund_etf_spot_em()

        # 选择需要的列
        selected_columns = [
            '代码', '名称', '最新价', 'IOPV实时估值', '涨跌幅', 
            '成交量', '成交额', '开盘价', '最高价', '最低价', 
            '昨收', '换手率', '流通市值', '总市值'
        ]
        
        # 只保留需要的列
        etf_df = etf_df[selected_columns]
        
        return etf_df
    except Exception as e:
        print(f"获取ETF列表失败：{str(e)}")
        return None

def save_etf_list(file_path='etf_list.csv'):
    """
    获取ETF列表并保存到CSV文件
    """
    etf_df = get_all_etfs()
    if etf_df is not None:
        # 保存到CSV文件
        etf_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"ETF列表已保存到：{file_path}")
        
        # 打印基本统计信息
        print(f"\nETF总数：{len(etf_df)}")
        print("\n涨跌幅前五名：")
        print(etf_df.nlargest(5, '涨跌幅')[['代码', '名称', '涨跌幅', '最新价']])  # 改为'最新价'
        print("\n成交额前五名：")
        print(etf_df.nlargest(5, '成交额')[['代码', '名称', '成交额', '最新价']])  # 改为'最新价'
    else:
        print("获取ETF列表失败")

if __name__ == '__main__':
    # 保存ETF列表到当前目录
    save_etf_list('/Users/admin/pythonwork/tushare/etf_list.csv')