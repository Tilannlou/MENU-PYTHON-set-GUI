"""
通用工具函数模块
提供系统中常用的工具函数，提高代码重用性
"""

import json
import re
import shlex
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

from .constants import (
    DEFAULT_WINDOW_SIZE, DEFAULT_POPUP_SIZE, DEFAULT_POPUP_OFFSET,
    HTTP_METHODS, ERROR_MESSAGES, WARNING_MESSAGES
)
from .logger import logger


def parse_size_string(size_str: str, default: str = DEFAULT_WINDOW_SIZE) -> Tuple[int, int]:
    """
    解析尺寸字符串为宽度和高度

    Args:
        size_str: 尺寸字符串，格式如 "800x600"
        default: 默认尺寸字符串

    Returns:
        (width, height) 元组
    """
    if not size_str:
        size_str = default

    try:
        width, height = size_str.split('x')
        return int(width), int(height)
    except (ValueError, AttributeError) as e:
        logger.warning(WARNING_MESSAGES['INVALID_SIZE_FORMAT'])
        return parse_size_string(default)


def parse_offset_string(offset_str: str) -> Tuple[int, int]:
    """
    解析偏移字符串为x和y偏移

    Args:
        offset_str: 偏移字符串，格式如 "50,50"

    Returns:
        (offset_x, offset_y) 元组
    """
    try:
        x, y = offset_str.split(',')
        return int(x), int(y)
    except (ValueError, AttributeError):
        return DEFAULT_POPUP_OFFSET


def parse_parameters(param_list: List[str]) -> Dict[str, str]:
    """
    解析参数列表为键值对字典

    Args:
        param_list: 参数列表，如 ["key1=value1", "key2=value2"]

    Returns:
        参数字典
    """
    params = {}
    for param in param_list:
        if '=' in param:
            key, value = param.split('=', 1)
            params[key.strip()] = value.strip('"\'')
    return params


def format_string_with_context(template: str, context: Dict[str, Any]) -> str:
    """
    使用上下文格式化字符串模板

    Args:
        template: 模板字符串
        context: 上下文字典

    Returns:
        格式化后的字符串
    """
    try:
        return template.format(**context)
    except (KeyError, ValueError) as e:
        logger.error(f"模板格式化失败: {e}")
        return template


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    安全地解析JSON字符串

    Args:
        json_str: JSON字符串
        default: 解析失败时的默认值

    Returns:
        解析后的对象或默认值
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON解析失败: {e}")
        return default


def safe_eval_expression(expression: str, context: Dict[str, Any]) -> Any:
    """
    安全地评估表达式

    Args:
        expression: 要评估的表达式
        context: 上下文变量字典

    Returns:
        评估结果
    """
    if not expression or not isinstance(expression, str):
        return None
        
    try:
        # 限制可用的内置函数
        safe_builtins = {
            'str': str, 'int': int, 'float': float, 'bool': bool,
            'len': len, 'min': min, 'max': max, 'abs': abs,
            'round': round, 'sum': sum
        }

        # 添加额外的安全检查
        if any(op in expression for op in ['import', 'exec', 'eval', 'open']):
            logger.warning(f"表达式包含危险操作: {expression}")
            return None
            
        # 预处理上下文，确保控件值被正确提取
        eval_context = {}
        for key, value in context.items():
            # 如果是控件，尝试获取其值
            if hasattr(value, 'get') and callable(getattr(value, 'get')):
                try:
                    eval_context[key] = value.get()
                except:
                    eval_context[key] = str(value)
            else:
                eval_context[key] = value

        return eval(expression, {"__builtins__": safe_builtins}, eval_context)
    except Exception as e:
        logger.error(f"表达式评估失败: {expression} - {e}")
        return None


def validate_http_method(method: str) -> bool:
    """
    验证HTTP方法是否有效

    Args:
        method: HTTP方法字符串

    Returns:
        是否有效
    """
    return method.upper() in HTTP_METHODS



def ensure_url_scheme(url: str, default_scheme: str = 'https') -> str:
    """確保URL包含協議方案，支持更多協議"""
    if not url:
        return f"{default_scheme}://localhost"
    
    # 檢查是否已經是完整URL
    parsed = urlparse(url)
    if parsed.scheme:
        return url
    
    # 支持本地AI模型常見的連接方式
    if url.startswith('localhost') or url.startswith('127.0.0.1'):
        return f"http://{url}"
    elif ':' in url and not url.startswith(('http://', 'https://')):
        # 可能是 host:port 格式
        return f"http://{url}"
    
    return f"{default_scheme}://{url}"

def join_url_path(base_url: str, path: str) -> str:
    """
    安全地拼接URL路径

    Args:
        base_url: 基础URL
        path: 要拼接的路径

    Returns:
        拼接后的URL
    """
    try:
        return urljoin(base_url, path)
    except Exception as e:
        logger.error(f"URL路径拼接失败: {e}")
        return base_url


def parse_command_line(line: str) -> List[str]:
    """
    解析命令行字符串为标记列表

    Args:
        line: 命令行字符串

    Returns:
        标记列表
    """
    # 移除 'menu' 前缀（如果存在）
    if line.startswith('menu '):
        line = line[5:]
    
    line = line.strip()
    if not line:
        return []
    
    try:
        # 尝试使用 shlex 解析
        return shlex.split(line)
    except ValueError as e:
        logger.warning(f"命令行解析失败: {e}")
        # 简单空格分割作为后备，同时处理引号内的内容
        tokens = []
        current_token = []
        in_quotes = False
        quote_char = None
        
        for char in line:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current_token.append(char)
            elif char == quote_char and in_quotes:
                in_quotes = False
                current_token.append(char)
                tokens.append(''.join(current_token).strip(quote_char))
                current_token = []
            elif char == ' ' and not in_quotes:
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
            else:
                current_token.append(char)
        
        if current_token:
            tokens.append(''.join(current_token))
        
        return tokens


def extract_target_from_args(args: List[str]) -> Tuple[List[str], Optional[str]]:
    """
    从参数列表中提取目标信息

    Args:
        args: 参数列表

    Returns:
        (剩余参数, 目标字符串) 元组
    """
    if '->' in args:
        arrow_index = args.index('->')
        if arrow_index + 1 < len(args):
            target = args[arrow_index + 1]
            remaining_args = args[:arrow_index]
            return remaining_args, target

    return args, None


def create_response_template(success: bool = True,
                           message: str = "",
                           data: Any = None,
                           status_code: int = 200) -> Dict[str, Any]:
    """
    创建标准响应模板

    Args:
        success: 是否成功
        message: 响应消息
        data: 响应数据
        status_code: 状态码

    Returns:
        响应字典
    """
    return {
        'success': success,
        'message': message,
        'data': data,
        'status_code': status_code
    }


def format_error_message(template: str, **kwargs) -> str:
    """
    格式化错误消息

    Args:
        template: 错误消息模板
        **kwargs: 格式化参数

    Returns:
        格式化后的错误消息
    """
    try:
        return template.format(**kwargs)
    except (KeyError, ValueError):
        return template


def validate_required_params(params: Dict[str, Any],
                           required_keys: List[str]) -> List[str]:
    """
    验证必需参数是否存在

    Args:
        params: 参数字典
        required_keys: 必需的键列表

    Returns:
        缺失的键列表
    """
    return [key for key in required_keys if key not in params or params[key] is None]


def merge_dictionaries(dict1: Dict[str, Any],
                      dict2: Dict[str, Any],
                      overwrite: bool = True) -> Dict[str, Any]:
    """
    合并两个字典

    Args:
        dict1: 第一个字典
        dict2: 第二个字典
        overwrite: 是否覆盖现有值

    Returns:
        合并后的字典
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if overwrite or key not in result:
            result[key] = value
    return result


def clamp_value(value: Union[int, float],
               min_value: Union[int, float],
               max_value: Union[int, float]) -> Union[int, float]:
    """
    限制数值在指定范围内

    Args:
        value: 要限制的数值
        min_value: 最小值
        max_value: 最大值

    Returns:
        限制后的数值
    """
    return max(min_value, min(value, max_value))


def generate_unique_id(prefix: str = "id", existing_ids: set = None) -> str:
    """
    生成唯一的ID

    Args:
        prefix: ID前缀
        existing_ids: 现有ID集合

    Returns:
        唯一的ID字符串
    """
    if existing_ids is None:
        existing_ids = set()

    counter = 1
    while True:
        new_id = f"{prefix}_{counter}"
        if new_id not in existing_ids:
            existing_ids.add(new_id)
            return new_id
        counter += 1


def deep_copy_dict(source_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度复制字典

    Args:
        source_dict: 源字典

    Returns:
        深度复制后的字典
    """
    try:
        return json.loads(json.dumps(source_dict))
    except (TypeError, ValueError):
        # 如果JSON序列化失败，使用递归复制
        return _recursive_copy(source_dict)


def _recursive_copy(obj: Any) -> Any:
    """递归复制对象"""
    if isinstance(obj, dict):
        return {key: _recursive_copy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_recursive_copy(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(_recursive_copy(item) for item in obj)
    else:
        return obj


def is_valid_identifier(name: str) -> bool:
    """
    检查字符串是否为有效的Python标识符

    Args:
        name: 要检查的字符串

    Returns:
        是否为有效标识符
    """
    return name.isidentifier() and not name.startswith('_')


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除无效字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换无效字符
    invalid_chars = '<>:"/\\|?*'
    sanitized = ''.join(c if c not in invalid_chars else '_' for c in filename)

    # 移除多余的空格和点
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'\.+', '.', sanitized)

    return sanitized.strip('_.')


def format_duration(seconds: float) -> str:
    """
    格式化持续时间

    Args:
        seconds: 秒数

    Returns:
        格式化后的时间字符串
    """
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"