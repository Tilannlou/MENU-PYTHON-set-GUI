"""
MENU002 核心模块包
提供GUI指令系统的核心功能
"""

from .command_registry import registry, CommandRegistry
from .menu_app import MenuApp
from .language_manager import LanguageManager, language_manager, get_text, set_language
from .api_manager import APIManager, api_manager, add_api, call_api, test_api_connection
from .ui_components import (
    DisplayArea, CodeDisplayArea, StatusBar, ToolBar, MenuBar,
    create_display_area, create_code_display_area,
    create_status_bar, create_toolbar, create_menubar
)
from .command_handlers import (
    cmd_clear, cmd_window, cmd_style, cmd_control, cmd_grid_setup,
    cmd_layout_grid, cmd_grid_position, cmd_relative_position, cmd_binding,
    cmd_exec, handle_api_setup, handle_api_call, cmd_display_area,
    cmd_display_content, cmd_clear_display, cmd_set_language,
    cmd_display_text, cmd_generate_code, cmd_execute_single_command
)

# 导出主要类和函数
__all__ = [
    # 类
    'CommandRegistry', 'MenuApp', 'LanguageManager', 'APIManager',
    'DisplayArea', 'CodeDisplayArea', 'StatusBar', 'ToolBar', 'MenuBar',
    
    # 实例
    'registry', 'language_manager', 'api_manager',
    
    # 函数
    'get_text', 'set_language', 'add_api', 'call_api', 'test_api_connection',
    'create_display_area', 'create_code_display_area',
    'create_status_bar', 'create_toolbar', 'create_menubar',
    
    # 命令处理器
    'cmd_clear', 'cmd_window', 'cmd_style', 'cmd_control', 'cmd_grid_setup',
    'cmd_layout_grid', 'cmd_grid_position', 'cmd_relative_position', 'cmd_binding',
    'cmd_exec', 'handle_api_setup', 'handle_api_call', 'cmd_display_area',
    'cmd_display_content', 'cmd_clear_display', 'cmd_set_language',
    'cmd_display_text', 'cmd_generate_code', 'cmd_execute_single_command'
]

__version__ = "2.0.0"
__author__ = "MENU002 Development Team"
__description__ = "優化版 GUI 指令系統核心模塊"