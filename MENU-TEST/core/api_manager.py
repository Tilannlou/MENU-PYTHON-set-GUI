"""
API管理模塊
提供API配置、調用和連接測試功能
"""

import json
import threading
from typing import Any, Dict, Optional, Union
import requests
from urllib.parse import urljoin

from utils.logger import logger
from utils.helpers import (
    ensure_url_scheme, join_url_path, format_string_with_context,
    safe_json_loads, validate_http_method, create_response_template
)
from utils.constants import (
    DEFAULT_API_TIMEOUT, DEFAULT_CONNECTION_TIMEOUT,
    HTTP_METHODS, ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES
)


class APIManager:
    """
    API管理器
    負責API配置管理、HTTP請求處理和連接測試
    """

    def __init__(self):
        self.apis: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def add_api(self, name: str, url: str, key: Optional[str] = None,
                username: Optional[str] = None, password: Optional[str] = None,
                show_secret: bool = False) -> bool:
        """
        添加或更新API配置

        Args:
            name: API名稱
            url: API基礎URL
            key: API金鑰（可選）
            username: 用戶名（可選）
            password: 密碼（可選）
            show_secret: 是否顯示敏感信息

        Returns:
            是否添加成功
        """
        with self._lock:
            try:
                # 確保URL包含協議
                url = ensure_url_scheme(url)

                self.apis[name] = {
                    'url': url,
                    'key': key,
                    'username': username,
                    'password': password,
                    'show_secret': show_secret
                }

                logger.info(f"API設定已更新: {name} -> {url}")
                return True

            except Exception as e:
                logger.error(f"添加API配置失敗: {name} - {e}")
                return False

    def remove_api(self, name: str) -> bool:
        """
        移除API配置

        Args:
            name: API名稱

        Returns:
            是否移除成功
        """
        with self._lock:
            if name in self.apis:
                del self.apis[name]
                logger.info(f"API配置已移除: {name}")
                return True
            else:
                logger.warning(f"未找到API配置: {name}")
                return False

    def get_api(self, name: str) -> Optional[Dict[str, Any]]:
        """
        獲取API配置

        Args:
            name: API名稱

        Returns:
            API配置字典或None
        """
        with self._lock:
            return self.apis.get(name)

    def list_apis(self) -> Dict[str, Dict[str, Any]]:
        """
        列出所有API配置

        Returns:
            API配置字典的副本
        """
        with self._lock:
            return self.apis.copy()

    def call_api(self, api_name: str, method: str, path: str,
                data_template: Optional[str] = None,
                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        呼叫API

        Args:
            api_name: API名稱
            method: HTTP方法
            path: API路徑
            data_template: 數據模板（可選）
            context: 上下文變量（可選）

        Returns:
            API響應結果
        """
        # 驗證HTTP方法
        if not validate_http_method(method):
            error_msg = ERROR_MESSAGES['INVALID_HTTP_METHOD'].format(method=method)
            logger.error(error_msg)
            return create_response_template(
                success=False,
                message=error_msg,
                status_code=400
            )

        # 獲取API配置
        api_config = self.get_api(api_name)
        if not api_config:
            error_msg = ERROR_MESSAGES['API_NOT_FOUND'].format(api_name=api_name)
            logger.error(error_msg)
            return create_response_template(
                success=False,
                message=error_msg,
                status_code=404
            )

        try:
            # 構建完整URL
            full_url = join_url_path(api_config['url'], path)

            # 準備請求頭
            headers = {"Content-Type": "application/json"}
            if api_config['key']:
                # 支援不同類型的授權頭
                if api_config['key'].startswith('Bearer '):
                    headers['Authorization'] = api_config['key']
                elif api_config['key'].startswith('Basic '):
                    headers['Authorization'] = api_config['key']
                else:
                    headers['Authorization'] = f"Bearer {api_config['key']}"

            # 準備請求體
            data = None
            if data_template and context:
                try:
                    # 替換模板中的變數
                    formatted_data = format_string_with_context(data_template, context)
                    data = safe_json_loads(formatted_data)

                    # 如果JSON解析失敗，嘗試作為純文字模板處理
                    if data is None:
                        data = formatted_data

                except Exception as e:
                    logger.error(f"數據模板處理失敗: {e}")
                    data = data_template

            # 發送請求
            method = method.upper()
            response = self._make_request(method, full_url, headers, data)

            # 處理響應
            return self._process_response(response, method, api_name, path)

        except Exception as e:
            error_msg = f"API請求失敗: {str(e)}"
            logger.error(f"{error_msg} ({api_name} {method} {path})")
            return create_response_template(
                success=False,
                message=error_msg,
                status_code=500
            )

    def _make_request(self, method: str, url: str, headers: Dict[str, str],
                     data: Any) -> requests.Response:
        """
        發送HTTP請求

        Args:
            method: HTTP方法
            url: 請求URL
            headers: 請求頭
            data: 請求數據

        Returns:
            響應對象
        """
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data,
                                      timeout=DEFAULT_API_TIMEOUT)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data,
                                       timeout=DEFAULT_API_TIMEOUT)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data,
                                      timeout=DEFAULT_API_TIMEOUT)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers,
                                         timeout=DEFAULT_API_TIMEOUT)
            else:
                raise ValueError(f"不支援的HTTP方法: {method}")

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP請求失敗: {e}")
            raise

    def _process_response(self, response: requests.Response, method: str,
                         api_name: str, path: str) -> Dict[str, Any]:
        """
        處理API響應

        Args:
            response: 響應對象
            method: HTTP方法
            api_name: API名稱
            path: 請求路徑

        Returns:
            處理後的響應結果
        """
        try:
            # 嘗試解析JSON響應
            try:
                result_data = response.json()
            except json.JSONDecodeError:
                result_data = {"response": response.text, "status_code": response.status_code}

            # 記錄成功調用
            logger.log_api_operation(api_name, method, path, success=True)

            return create_response_template(
                success=True,
                message=SUCCESS_MESSAGES['API_CONNECTED'],
                data=result_data,
                status_code=response.status_code
            )

        except Exception as e:
            error_msg = f"響應處理失敗: {str(e)}"
            logger.error(f"{error_msg} ({api_name} {method} {path})")
            return create_response_template(
                success=False,
                message=error_msg,
                status_code=response.status_code if 'response' in locals() else 500
            )

    def test_connection(self, api_name: str) -> Dict[str, Any]:
        """
        測試API連接

        Args:
            api_name: API名稱

        Returns:
            連接測試結果
        """
        api_config = self.get_api(api_name)
        if not api_config:
            error_msg = ERROR_MESSAGES['API_NOT_FOUND'].format(api_name=api_name)
            logger.error(error_msg)
            return create_response_template(
                success=False,
                message=error_msg,
                status_code=404
            )

        try:
            # 嘗試連接API根路徑
            response = requests.get(api_config['url'], timeout=DEFAULT_CONNECTION_TIMEOUT)

            success = response.status_code == 200
            message = (SUCCESS_MESSAGES['CONNECTION_SUCCESS']
                      if success else f"連接失敗: {response.status_code}")

            logger.log_api_operation(api_name, 'GET', '/', success=success)

            return create_response_template(
                success=success,
                message=message,
                data={
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                },
                status_code=response.status_code
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"連接測試失敗: {str(e)}"
            logger.error(f"{error_msg} ({api_name})")
            return create_response_template(
                success=False,
                message=error_msg,
                status_code=500
            )

    def update_api_auth(self, api_name: str, key: Optional[str] = None,
                       username: Optional[str] = None,
                       password: Optional[str] = None) -> bool:
        """
        更新API認證信息

        Args:
            api_name: API名稱
            key: API金鑰（可選）
            username: 用戶名（可選）
            password: 密碼（可選）

        Returns:
            是否更新成功
        """
        with self._lock:
            if api_name not in self.apis:
                logger.warning(f"未找到API配置: {api_name}")
                return False

            api_config = self.apis[api_name]

            if key is not None:
                api_config['key'] = key
            if username is not None:
                api_config['username'] = username
            if password is not None:
                api_config['password'] = password

            logger.info(f"API認證信息已更新: {api_name}")
            return True

    def clear_all_apis(self):
        """清除所有API配置"""
        with self._lock:
            self.apis.clear()
            logger.info("所有API配置已清除")

    def get_api_count(self) -> int:
        """
        獲取API配置數量

        Returns:
            API配置數量
        """
        with self._lock:
            return len(self.apis)

    def export_api_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        導出所有API配置

        Returns:
            API配置字典的副本
        """
        with self._lock:
            return self.apis.copy()

    def import_api_configs(self, configs: Dict[str, Dict[str, Any]],
                          overwrite: bool = True) -> int:
        """
        導入API配置

        Args:
            configs: API配置字典
            overwrite: 是否覆蓋現有配置

        Returns:
            成功導入的配置數量
        """
        with self._lock:
            success_count = 0

            for name, config in configs.items():
                if overwrite or name not in self.apis:
                    try:
                        self.apis[name] = config.copy()
                        success_count += 1
                        logger.debug(f"導入API配置: {name}")
                    except Exception as e:
                        logger.error(f"導入API配置失敗: {name} - {e}")

            logger.info(f"API配置導入完成: {success_count}/{len(configs)}")
            return success_count


# 全局API管理器實例
api_manager = APIManager()


def add_api(name: str, url: str, **kwargs) -> bool:
    """
    添加API的便捷函數

    Args:
        name: API名稱
        url: API URL
        **kwargs: 其他參數

    Returns:
        是否添加成功
    """
    return api_manager.add_api(name, url, **kwargs)


def call_api(api_name: str, method: str, path: str, **kwargs) -> Dict[str, Any]:
    """
    呼叫API的便捷函數

    Args:
        api_name: API名稱
        method: HTTP方法
        path: API路徑
        **kwargs: 其他參數

    Returns:
        API響應結果
    """
    return api_manager.call_api(api_name, method, path, **kwargs)


def test_api_connection(api_name: str) -> Dict[str, Any]:
    """
    測試API連接的便捷函數

    Args:
        api_name: API名稱

    Returns:
        連接測試結果
    """
    return api_manager.test_connection(api_name)