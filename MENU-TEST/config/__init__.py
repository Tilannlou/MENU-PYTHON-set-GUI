# config/__init__.py
"""
MENU002 配置模塊包
提供配置管理功能
"""

import os
import json
from pathlib import Path

def load_config(config_path: str) -> dict:
    """加載配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加載配置文件失敗: {e}")
        return {}

def save_config(config: dict, config_path: str):
    """保存配置文件"""
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"保存配置文件失敗: {e}")

__all__ = ['load_config', 'save_config']
