import os
import logging
from logging.handlers import RotatingFileHandler

class LoggerManager:
    """
    日志管理工具类，用于为不同的股票代码创建独立的日志记录器
    """
    
    # 日志记录器缓存
    _loggers = {}
    
    @classmethod
    def setup_log_dir(cls):
        """设置日志目录"""
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    @classmethod
    def get_logger(cls, ts_code):
        """
        获取指定股票代码的日志记录器
        
        参数：
            ts_code: 股票或ETF代码
        """
        if ts_code in cls._loggers:
            return cls._loggers[ts_code]
        
        # 创建新的日志记录器
        logger = logging.getLogger(f"etf_monitor_{ts_code}")
        logger.setLevel(logging.INFO)
        
        # 防止日志重复输出
        if not logger.handlers:
            # 创建日志目录
            log_dir = cls.setup_log_dir()
            
            # 创建文件处理器，使用 RotatingFileHandler 限制文件大小
            log_file = os.path.join(log_dir, f"{ts_code}.log")
            file_handler = RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            
            # 设置日志格式
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # 添加处理器到日志记录器
            logger.addHandler(file_handler)
            
            # 同时输出到控制台
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # 缓存日志记录器
        cls._loggers[ts_code] = logger
        return logger