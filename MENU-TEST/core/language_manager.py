"""
多語言管理模塊
提供多語言支持和翻譯功能
"""

from typing import Dict, Optional
from utils.logger import logger
from utils.constants import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE


class LanguageManager:
    """
    多語言管理器
    支持多種語言的翻譯和切換
    """

    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {
            "en": {
                "welcome": "Welcome to MENU002",
                "api_connected": "API Connected",
                "error": "Error",
                "success": "Success",
                "ready": "Ready",
                "loading": "Loading...",
                "complete": "Complete",
                "button_ok": "OK",
                "button_cancel": "Cancel",
                "button_close": "Close",
                "button_save": "Save",
                "button_load": "Load",
                "button_clear": "Clear",
                "button_test": "Test",
                "label_status": "Status",
                "label_result": "Result",
                "label_message": "Message",
                "menu_file": "File",
                "menu_edit": "Edit",
                "menu_view": "View",
                "menu_help": "Help",
                "window_title": "Application",
                "popup_title": "Dialog",
                "error_title": "Error",
                "warning_title": "Warning",
                "info_title": "Information",
                "confirm_title": "Confirm",
                "input_prompt": "Please enter:",
                "select_prompt": "Please select:",
                "processing": "Processing...",
                "connecting": "Connecting...",
                "disconnected": "Disconnected",
                "timeout": "Timeout",
                "network_error": "Network Error",
                "invalid_input": "Invalid Input",
                "operation_failed": "Operation Failed",
                "operation_success": "Operation Successful",
                "data_saved": "Data Saved",
                "data_loaded": "Data Loaded",
                "settings_saved": "Settings Saved",
                "settings_loaded": "Settings Loaded",
                "language_changed": "Language Changed",
                "theme_changed": "Theme Changed",
                "layout_updated": "Layout Updated",
                "control_created": "Control Created",
                "control_updated": "Control Updated",
                "control_deleted": "Control Deleted",
                "window_created": "Window Created",
                "window_closed": "Window Closed",
                "popup_opened": "Popup Opened",
                "popup_closed": "Popup Closed",
                "api_call_success": "API Call Successful",
                "api_call_failed": "API Call Failed",
                "connection_success": "Connection Successful",
                "connection_failed": "Connection Failed",
                "test_passed": "Test Passed",
                "test_failed": "Test Failed"
            },
            "zh-TW": {
                "welcome": "歡迎使用 MENU002",
                "api_connected": "API 已連接",
                "error": "錯誤",
                "success": "成功",
                "ready": "就緒",
                "loading": "載入中...",
                "complete": "完成",
                "button_ok": "確定",
                "button_cancel": "取消",
                "button_close": "關閉",
                "button_save": "儲存",
                "button_load": "載入",
                "button_clear": "清除",
                "button_test": "測試",
                "label_status": "狀態",
                "label_result": "結果",
                "label_message": "訊息",
                "menu_file": "檔案",
                "menu_edit": "編輯",
                "menu_view": "檢視",
                "menu_help": "說明",
                "window_title": "應用程式",
                "popup_title": "對話框",
                "error_title": "錯誤",
                "warning_title": "警告",
                "info_title": "資訊",
                "confirm_title": "確認",
                "input_prompt": "請輸入：",
                "select_prompt": "請選擇：",
                "processing": "處理中...",
                "connecting": "連線中...",
                "disconnected": "已斷線",
                "timeout": "逾時",
                "network_error": "網路錯誤",
                "invalid_input": "無效輸入",
                "operation_failed": "操作失敗",
                "operation_success": "操作成功",
                "data_saved": "資料已儲存",
                "data_loaded": "資料已載入",
                "settings_saved": "設定已儲存",
                "settings_loaded": "設定已載入",
                "language_changed": "語言已變更",
                "theme_changed": "主題已變更",
                "layout_updated": "佈局已更新",
                "control_created": "控件已建立",
                "control_updated": "控件已更新",
                "control_deleted": "控件已刪除",
                "window_created": "視窗已建立",
                "window_closed": "視窗已關閉",
                "popup_opened": "彈出視窗已開啟",
                "popup_closed": "彈出視窗已關閉",
                "api_call_success": "API 呼叫成功",
                "api_call_failed": "API 呼叫失敗",
                "connection_success": "連線成功",
                "connection_failed": "連線失敗",
                "test_passed": "測試通過",
                "test_failed": "測試失敗"
            },
            "zh-CN": {
                "welcome": "欢迎使用 MENU002",
                "api_connected": "API 已连接",
                "error": "错误",
                "success": "成功",
                "ready": "就绪",
                "loading": "载入中...",
                "complete": "完成",
                "button_ok": "确定",
                "button_cancel": "取消",
                "button_close": "关闭",
                "button_save": "保存",
                "button_load": "载入",
                "button_clear": "清除",
                "button_test": "测试",
                "label_status": "状态",
                "label_result": "结果",
                "label_message": "消息",
                "menu_file": "文件",
                "menu_edit": "编辑",
                "menu_view": "视图",
                "menu_help": "帮助",
                "window_title": "应用程序",
                "popup_title": "对话框",
                "error_title": "错误",
                "warning_title": "警告",
                "info_title": "信息",
                "confirm_title": "确认",
                "input_prompt": "请输入：",
                "select_prompt": "请选择：",
                "processing": "处理中...",
                "connecting": "连接中...",
                "disconnected": "已断开",
                "timeout": "超时",
                "network_error": "网络错误",
                "invalid_input": "无效输入",
                "operation_failed": "操作失败",
                "operation_success": "操作成功",
                "data_saved": "数据已保存",
                "data_loaded": "数据已载入",
                "settings_saved": "设置已保存",
                "settings_loaded": "设置已载入",
                "language_changed": "语言已变更",
                "theme_changed": "主题已变更",
                "layout_updated": "布局已更新",
                "control_created": "控件已建立",
                "control_updated": "控件已更新",
                "control_deleted": "控件已删除",
                "window_created": "窗口已建立",
                "window_closed": "窗口已关闭",
                "popup_opened": "弹出窗口已开启",
                "popup_closed": "弹出窗口已关闭",
                "api_call_success": "API 调用成功",
                "api_call_failed": "API 调用失败",
                "connection_success": "连接成功",
                "connection_failed": "连接失败",
                "test_passed": "测试通过",
                "test_failed": "测试失败"
            }
        }
        self.current_lang = DEFAULT_LANGUAGE

    def set_language(self, lang_code: str) -> bool:
        """
        設定當前語言

        Args:
            lang_code: 語言代碼

        Returns:
            是否設定成功
        """
        if lang_code in self.translations:
            self.current_lang = lang_code
            logger.info(f"語言已設定為: {lang_code}")
            return True
        else:
            logger.warning(f"不支援的語言: {lang_code}")
            return False

    def get_text(self, key: str, lang_code: Optional[str] = None) -> str:
        """
        獲取翻譯文字

        Args:
            key: 翻譯鍵
            lang_code: 語言代碼（可選，默認使用當前語言）

        Returns:
            翻譯後的文字，如果找不到則返回鍵本身
        """
        lang = lang_code or self.current_lang

        if lang in self.translations and key in self.translations[lang]:
            return self.translations[lang][key]
        else:
            logger.debug(f"未找到翻譯: {lang}.{key}")
            return key

    def get_current_language(self) -> str:
        """
        獲取當前語言代碼

        Returns:
            當前語言代碼
        """
        return self.current_lang

    def get_available_languages(self) -> Dict[str, str]:
        """
        獲取所有可用的語言

        Returns:
            語言代碼到語言名稱的映射
        """
        return {
            "en": "English",
            "zh-TW": "繁體中文",
            "zh-CN": "简体中文"
        }

    def add_translation(self, lang_code: str, translations: Dict[str, str]):
        """
        添加新的語言翻譯

        Args:
            lang_code: 語言代碼
            translations: 翻譯字典
        """
        if lang_code not in self.translations:
            self.translations[lang_code] = {}

        self.translations[lang_code].update(translations)
        logger.info(f"添加語言翻譯: {lang_code} ({len(translations)} 項)")

    def remove_translation(self, lang_code: str):
        """
        移除語言翻譯

        Args:
            lang_code: 語言代碼
        """
        if lang_code in self.translations:
            del self.translations[lang_code]
            logger.info(f"移除語言翻譯: {lang_code}")

    def has_translation(self, key: str, lang_code: Optional[str] = None) -> bool:
        """
        檢查是否存在指定鍵的翻譯

        Args:
            key: 翻譯鍵
            lang_code: 語言代碼（可選，默認使用當前語言）

        Returns:
            是否存在翻譯
        """
        lang = lang_code or self.current_lang
        return lang in self.translations and key in self.translations[lang]

    def get_translation_count(self, lang_code: Optional[str] = None) -> int:
        """
        獲取指定語言的翻譯項數量

        Args:
            lang_code: 語言代碼（可選，默認使用當前語言）

        Returns:
            翻譯項數量
        """
        lang = lang_code or self.current_lang
        return len(self.translations.get(lang, {}))

    def export_translations(self, lang_code: Optional[str] = None) -> Dict[str, str]:
        """
        導出指定語言的翻譯

        Args:
            lang_code: 語言代碼（可選，默認使用當前語言）

        Returns:
            翻譯字典
        """
        lang = lang_code or self.current_lang
        return self.translations.get(lang, {}).copy()

    def import_translations(self, lang_code: str, translations: Dict[str, str],
                          overwrite: bool = False):
        """
        導入翻譯

        Args:
            lang_code: 語言代碼
            translations: 要導入的翻譯字典
            overwrite: 是否覆蓋現有翻譯
        """
        if lang_code not in self.translations:
            self.translations[lang_code] = {}

        for key, value in translations.items():
            if overwrite or key not in self.translations[lang_code]:
                self.translations[lang_code][key] = value

        logger.info(f"導入翻譯: {lang_code} ({len(translations)} 項)")


# 全局語言管理器實例
language_manager = LanguageManager()


def get_text(key: str, lang_code: Optional[str] = None) -> str:
    """
    獲取翻譯文字的便捷函數

    Args:
        key: 翻譯鍵
        lang_code: 語言代碼（可選）

    Returns:
        翻譯後的文字
    """
    return language_manager.get_text(key, lang_code)


def set_language(lang_code: str) -> bool:
    """
    設定語言的便捷函數

    Args:
        lang_code: 語言代碼

    Returns:
        是否設定成功
    """
    return language_manager.set_language(lang_code)