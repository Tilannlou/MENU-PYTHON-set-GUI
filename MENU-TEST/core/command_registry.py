"""
指令註冊系統模塊
提供指令註冊、查找和管理功能
"""

from typing import Any, Callable, Dict, Optional
from utils.logger import logger


class CommandRegistry:
    """
    指令註冊系統
    支持指令註冊、別名管理和動態查找
    """

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}

    def register(self, name: str) -> Callable:
        """
        註冊指令處理器的裝飾器

        Args:
            name: 指令名稱

        Returns:
            裝飾器函數
        """
        def decorator(func: Callable) -> Callable:
            """裝飾器實現"""
            self.handlers[name.lower()] = func
            logger.debug(f"註冊指令處理器: {name} -> {func.__name__}")
            return func
        return decorator

    def get(self, name: str) -> Optional[Callable]:
        """
        獲取指令處理器

        Args:
            name: 指令名稱

        Returns:
            指令處理器函數或None
        """
        # 首先嘗試直接查找
        handler = self.handlers.get(name.lower())
        if handler:
            return handler

        # 如果找不到，嘗試別名查找
        actual_name = self.aliases.get(name.lower())
        if actual_name:
            handler = self.handlers.get(actual_name.lower())
            if handler:
                logger.debug(f"使用別名找到處理器: {name} -> {actual_name}")
                return handler

        logger.warning(f"未找到指令處理器: {name}")
        return None

    def add_alias(self, alias: str, actual_name: str):
        """
        添加指令別名

        Args:
            alias: 別名
            actual_name: 實際指令名
        """
        self.aliases[alias.lower()] = actual_name.lower()
        logger.debug(f"添加指令別名: {alias} -> {actual_name}")

    def list_commands(self) -> Dict[str, Callable]:
        """
        列出所有註冊的指令

        Returns:
            指令字典
        """
        return self.handlers.copy()

    def list_aliases(self) -> Dict[str, str]:
        """
        列出所有別名

        Returns:
            別名字典
        """
        return self.aliases.copy()

    def has_command(self, name: str) -> bool:
        """
        檢查是否存在指定指令

        Args:
            name: 指令名稱

        Returns:
            是否存在
        """
        return name.lower() in self.handlers or name.lower() in self.aliases

    def remove_command(self, name: str) -> bool:
        """
        移除指令處理器

        Args:
            name: 指令名稱

        Returns:
            是否成功移除
        """
        name_lower = name.lower()
        if name_lower in self.handlers:
            del self.handlers[name_lower]
            logger.debug(f"移除指令處理器: {name}")
            return True

        # 檢查是否是別名
        if name_lower in self.aliases:
            del self.aliases[name_lower]
            logger.debug(f"移除指令別名: {name}")
            return True

        return False

    def clear(self):
        """清除所有指令和別名"""
        self.handlers.clear()
        self.aliases.clear()
        logger.debug("清除所有指令註冊信息")

    def execute(self, name: str, *args, **kwargs) -> Any:
        """
        執行指令

        Args:
            name: 指令名稱
            *args: 位置參數
            **kwargs: 關鍵字參數

        Returns:
            執行結果

        Raises:
            ValueError: 指令不存在時拋出
        """
        handler = self.get(name)
        if not handler:
            raise ValueError(f"未找到指令: {name}")

        try:
            logger.log_command(name, args, kwargs)
            result = handler(*args, **kwargs)
            logger.debug(f"指令執行成功: {name}")
            return result
        except Exception as e:
            logger.error(f"指令執行失敗: {name} - {e}")
            raise


# 全局指令註冊器實例
registry = CommandRegistry()


def register_command(name: str) -> Callable:
    """
    註冊指令的便捷函數

    Args:
        name: 指令名稱

    Returns:
        裝飾器函數
    """
    return registry.register(name)


def get_command(name: str) -> Optional[Callable]:
    """
    獲取指令的便捷函數

    Args:
        name: 指令名稱

    Returns:
        指令處理器或None
    """
    return registry.get(name)


def execute_command(name: str, *args, **kwargs) -> Any:
    """
    執行指令的便捷函數

    Args:
        name: 指令名稱
        *args: 位置參數
        **kwargs: 關鍵字參數

    Returns:
        執行結果
    """
    return registry.execute(name, *args, **kwargs)