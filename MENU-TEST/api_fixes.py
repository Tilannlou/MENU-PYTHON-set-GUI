# api_fixes.py
"""
API 連接增強補丁
提供更靈活的API連接方案
"""

def create_flexible_api_manager():
    """創建靈活的API管理器實例"""
    from core.api_manager import APIManager
    
    class FlexibleAPIManager(APIManager):
        def call_api_with_fallback(self, api_name: str, method: str, path: str,
                                 fallback_url: str = None, **kwargs):
            """支持備用URL的API調用"""
            try:
                return self.call_api(api_name, method, path, **kwargs)
            except Exception as e:
                if fallback_url:
                    # 使用備用URL重試
                    original_config = self.get_api(api_name)
                    self.add_api(f"{api_name}_fallback", fallback_url)
                    result = self.call_api(f"{api_name}_fallback", method, path, **kwargs)
                    # 恢復原始配置
                    self.add_api(api_name, original_config['url'])
                    return result
                raise
    
    return FlexibleAPIManager()