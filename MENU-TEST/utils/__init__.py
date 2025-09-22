"""
MENU002 工具模块包
提供通用的工具函数和常量
"""

from .logger import logger, configure_logging, LOG_LEVELS, log_execution_time, log_exceptions
from .helpers import (
    parse_size_string, parse_parameters, format_string_with_context,
    safe_eval_expression, validate_http_method, ensure_url_scheme,
    parse_command_line, create_response_template, generate_unique_id
)
from .constants import (
    HTTP_METHODS, DEFAULT_WINDOW_SIZE, CONTROL_TYPES, EVENT_TYPES,
    ANCHOR_POINTS, STICKY_DIRECTIONS, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE,
    DEFAULT_COLORS, DEFAULT_FONTS, ERROR_MESSAGES, SUCCESS_MESSAGES,
    WARNING_MESSAGES, COMMAND_ALIASES, PROCESSING_ORDER, CONFIG_FILES, PATHS
)

__all__ = [
    # 日志相关
    'logger', 'configure_logging', 'LOG_LEVELS', 'log_execution_time', 'log_exceptions',
    
    # 工具函数
    'parse_size_string', 'parse_parameters', 'format_string_with_context',
    'safe_eval_expression', 'validate_http_method', 'ensure_url_scheme',
    'parse_command_line', 'create_response_template', 'generate_unique_id',
    
    # 常量
    'HTTP_METHODS', 'DEFAULT_WINDOW_SIZE', 'CONTROL_TYPES', 'EVENT_TYPES',
    'ANCHOR_POINTS', 'STICKY_DIRECTIONS', 'SUPPORTED_LANGUAGES', 'DEFAULT_LANGUAGE',
    'DEFAULT_COLORS', 'DEFAULT_FONTS', 'ERROR_MESSAGES', 'SUCCESS_MESSAGES',
    'WARNING_MESSAGES', 'COMMAND_ALIASES', 'PROCESSING_ORDER', 'CONFIG_FILES', 'PATHS'
]

__version__ = "2.0.0"