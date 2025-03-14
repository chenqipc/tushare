import requests
import pandas as pd
from datetime import datetime, timedelta
import json

class EastMoneyAPI:
    """东方财富数据接口封装"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
    def get_market_id(self, symbol, security_type='ETF'):
        """
        获取证券的市场代码
        参数:
            symbol: 证券代码
            security_type: 证券类型，支持 'ETF' 或 'STOCK'
        返回: 
            (市场代码, 完整symbol)
            市场代码: 1-上海，0-深圳
        """
        try:
            # 上海证券交易所
            if symbol.startswith(('60', '68', '51', '58', '50', '56')):
                return '1', f"1.{symbol}"
            # 深圳证券交易所
            elif symbol.startswith(('00', '30', '15', '16', '12', '39')):
                return '0', f"0.{symbol}"
            
            # 如果通过前缀无法判断，则尝试通过API查询
            print(f"无法通过代码前缀判断 {symbol} 的市场，尝试通过API查询...")
            
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            
            if security_type == 'ETF':
                fs = "b:MK0021,b:MK0022,b:MK0023,b:MK0024"
            else:
                fs = "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2"
            
            params = {
                "pn": "1",
                "pz": "10000",
                "po": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fid": "f3",
                "fs": fs,
                "fields": "f12,f13,f14"
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if 'data' in data and 'diff' in data['data']:
                for item in data['data']['diff']:
                    if item['f12'] == symbol:
                        return item['f13'], f"{item['f13']}.{symbol}"
            
            # 如果在列表中未找到，则依次尝试沪深市场
            for market_id in ['1', '0']:
                test_url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
                test_params = {
                    "fields1": "f1",
                    "fields2": "f51",
                    "klt": "101",
                    "fqt": "1",
                    "secid": f"{market_id}.{symbol}",
                    "beg": "20200101",
                    "end": "20500101",
                }
                
                response = requests.get(test_url, params=test_params, headers=self.headers)
                data = response.json()
                
                if 'data' in data and data['data']['klines']:
                    return market_id, f"{market_id}.{symbol}"
                    
            print(f"未找到 {symbol} 的市场信息")
            return None, None
        except Exception as e:
            print(f"获取市场信息失败：{str(e)}")
            return None, None
    
    def get_daily_data(self, symbol, start_date=None, end_date=None):
        """获取日线数据"""
        try:
            # 如果传入的是完整代码（带市场标识），则直接分割使用
            if '.' in symbol:
                market_id, code = symbol.split('.')
            else:
                # 否则获取市场ID
                market_id, _ = self.get_market_id(symbol)
                code = symbol
                
            if not market_id:
                return None
                
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                "klt": "101",  # 日线
                "fqt": "1",    # 前复权
                "secid": f"{market_id}.{code}",
                "beg": start_date if start_date else "20200101",
                "end": end_date if end_date else "20500101",
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if 'data' not in data or not data['data']['klines']:
                print(f"未找到 {symbol} 的日线数据")
                return None
            
            klines = data['data']['klines']
            rows = [line.split(',') for line in klines]
            df = pd.DataFrame(rows, columns=[
                'trade_date', 'open', 'close', 'high', 'low',
                'vol', 'amount', 'amplitude'
            ])
            
            # 转换数据类型
            for col in ['open', 'close', 'high', 'low', 'vol', 'amount']:
                df[col] = pd.to_numeric(df[col])
                
            return df
        except Exception as e:
            print(f"获取日线数据失败：{str(e)}")
            return None
            
    def get_minute_data(self, symbol, period, start_date=None, end_date=None):
        """获取分钟线数据"""
        try:
            # 如果传入的是完整代码（带市场标识），则直接分割使用
            if '.' in symbol:
                market_id, code = symbol.split('.')
            else:
                # 否则获取市场ID
                market_id, _ = self.get_market_id(symbol)
                code = symbol
                
            if not market_id:
                return None
                
            period_map = {
                '1min': '1', '5min': '5', '15min': '15',
                '30min': '30', '60min': '60'
            }
            
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                "klt": period_map.get(period, '1'),
                "fqt": "1",
                "secid": f"{market_id}.{code}",
                "beg": start_date if start_date else "20200101",
                "end": end_date if end_date else "20500101",
            }
            
            response = requests.get(url, params=params, headers=self.headers)
            data = response.json()
            
            if 'data' not in data or not data['data']['klines']:
                # 尝试沪市代码
                params['secid'] = f"1.{symbol}"
                response = requests.get(url, params=params, headers=self.headers)
                data = response.json()
                
                if 'data' not in data or not data['data']['klines']:
                    print(f"未找到 {symbol} 的数据")
                    return None
            
            klines = data['data']['klines']
            rows = [line.split(',') for line in klines]
            df = pd.DataFrame(rows, columns=[
                'trade_time', 'open', 'close', 'high', 'low',
                'vol', 'amount', 'amplitude'
            ])
            
            # 转换数据类型
            for col in ['open', 'close', 'high', 'low', 'vol', 'amount']:
                df[col] = pd.to_numeric(df[col])
                
            return df
        except Exception as e:
            print(f"获取分钟线数据失败：{str(e)}")
            return None
            
    def merge_60min_to_120min(self, symbol, start_date=None, end_date=None):
        """合并60分钟数据为120分钟数据"""
        df = self.get_minute_data(symbol, '60min', start_date, end_date)
        if df is not None and not df.empty:
            df = df.sort_values('trade_time')
            df['group'] = df.index // 2
            df = df.groupby('group').agg({
                'trade_time': 'first',
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'vol': 'sum',
                'amount': 'sum'
            }).reset_index(drop=True)
        return df

if __name__ == '__main__':
    api = EastMoneyAPI()
    
    # 测试创业板ETF
    etf_symbol = '512980'
    market_id, full_symbol = api.get_market_id(etf_symbol, 'ETF')
    print(f"ETF市场信息：市场代码={market_id}, 完整代码={full_symbol}")
    
    # 计算三个月前的日期
    start_date = (datetime.today() - timedelta(days=90)).strftime('%Y%m%d')
    end_date = datetime.today().strftime('%Y%m%d')
    
    print(f"获取从 {start_date} 到 {end_date} 的分钟数据")
    df = api.get_minute_data(etf_symbol, '60min', start_date, end_date)
    print(df)