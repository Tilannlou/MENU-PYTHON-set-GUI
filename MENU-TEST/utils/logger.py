# logger.py 修改部分
import os
import platform
from pathlib import Path

# 修改 _setup_handlers 方法中的路径处理
def _setup_handlers(self):
    """設置日誌處理器"""
    # 創建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(self.log_level)
    console_handler.setFormatter(formatter)
    self.logger.addHandler(console_handler)

    # 文件處理器 - 改进路径处理
    try:
        # 获取当前目录
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