# logger.py - 完整修复版本
import os
import sys
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# 导入常量（确保constants.py中有PATHS定义）
try:
    from .constants import PATHS, LOG_LEVELS
except ImportError:
    # 如果导入失败，提供默认值
    PATHS = {
        'CONFIG_DIR': 'config',
        'EXAMPLES_DIR': 'examples', 
        'PLUGINS_DIR': 'plugins',
        'LOGS_DIR': 'logs'
    }
    LOG_LEVELS = {
        'DEBUG': 'DEBUG',
        'INFO': 'INFO',
        'WARNING': 'WARNING',
        'ERROR': 'ERROR',
        'CRITICAL': 'CRITICAL'
    }


class MenuLogger:
    """
    MENU002 自定义日志系统
    提供分级日志记录和灵活的日志处理
    """
    
    def __init__(self, name: str = "MENU002", log_level: str = "INFO"):
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        
        # 移除可能存在的现有处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        self._setup_handlers()
        
    def _setup_handlers(self):
        """設置日誌處理器"""
        # 創建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台處理器 - 使用安全的編碼處理
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)

        # 創建安全的格式器，避免編碼錯誤
        safe_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(safe_formatter)

        # 設置錯誤處理
        console_handler.handleError = self._handle_console_error
        self.logger.addHandler(console_handler)

        # 文件處理器 - 改进路径处理
        try:
            # 获取当前目录 - 更健壮的路径处理
            current_dir = Path(__file__).parent.parent
            log_dir = current_dir / PATHS['LOGS_DIR']
            
            # 确保日志目录存在
            log_dir.mkdir(exist_ok=True, parents=True)

            log_file = log_dir / f"menu002_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            self.logger.info(f"日誌文件已創建: {log_file}")
        except Exception as e:
            self.logger.warning(f"無法創建日誌文件: {e}")
            # 添加回退到控制台日志
            fallback_handler = logging.StreamHandler(sys.stderr)
            fallback_handler.setLevel(logging.ERROR)
            fallback_handler.setFormatter(formatter)
            self.logger.addHandler(fallback_handler)

    def _handle_console_error(self, record):
        """處理控制台編碼錯誤"""
        try:
            # 嘗試使用替代編碼
            import codecs
            # 簡單地忽略編碼錯誤，繼續執行
            pass
        except Exception:
            # 如果處理失敗，則靜默繼續
            pass

    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
        
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(message, *args, **kwargs)
        
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)
        
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)
        
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, *args, **kwargs)
        
    def log_api_operation(self, api_name: str, method: str, path: str, success: bool = True):
        """记录API操作日志"""
        status = "成功" if success else "失败"
        self.info(f"API操作: {api_name} {method} {path} - {status}")
        
    def log_command(self, command: str, args: tuple, kwargs: dict):
        """记录命令执行日志"""
        self.debug(f"执行命令: {command} 参数: {args} 关键字参数: {kwargs}")


# 全局日志实例
logger = MenuLogger()

# 配置函数
def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    配置日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径（可选）
    """
    global logger
    logger = MenuLogger(log_level=log_level)
    
    if log_file:
        try:
            # 添加额外的文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
            logger.logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"无法创建日志文件 {log_file}: {e}")


# 便捷函数
def get_logger(name: str = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 记录器名称
        
    Returns:
        日志记录器实例
    """
    if name:
        return logging.getLogger(name)
    return logger.logger


def set_log_level(level: str):
    """
    设置日志级别
    
    Args:
        level: 日志级别
    """
    level = getattr(logging, level.upper(), logging.INFO)
    logger.logger.setLevel(level)
    for handler in logger.logger.handlers:
        handler.setLevel(level)


# 性能监控装饰器
def log_execution_time(func):
    """记录函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        logger.debug(f"函数 {func.__name__} 执行时间: {execution_time:.3f}秒")
        return result
    return wrapper


# 错误处理装饰器  
def log_exceptions(func):
    """记录异常的装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行出错: {str(e)}", exc_info=True)
            raise
    return wrapper


if __name__ == "__main__":
    # 测试日志系统
    logger.info("日志系统测试开始")
    logger.debug("这是一条调试信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.info("日志系统测试结束")