"""
常量定義模塊
定義系統中使用的各種常量，提高代碼可維護性
"""

# HTTP 方法常量
HTTP_METHODS = {'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'}

# 默認配置常量
DEFAULT_WINDOW_SIZE = "800x600"
DEFAULT_POPUP_SIZE = "400x300"
DEFAULT_POPUP_OFFSET = (50, 50)
DEFAULT_API_TIMEOUT = 30
DEFAULT_CONNECTION_TIMEOUT = 10

# 控件類型常量
CONTROL_TYPES = {
    'BUTTON': 'button',
    'LABEL': 'label',
    'ENTRY': 'entry',
    'TEXT': 'text',
    'EDIT': 'edit'
}

# 事件類型常量
EVENT_TYPES = {
    'CLICK': 'click',
    'DOUBLE_CLICK': 'doubleclick',
    'KEY_RELEASE': 'keyrelease',
    'MOUSE_ENTER': 'mouse_enter',
    'MOUSE_LEAVE': 'mouse_leave'
}

# 錨點常量
ANCHOR_POINTS = {
    'NW': 'nw', 'N': 'n', 'NE': 'ne',
    'W': 'w', 'CENTER': 'center', 'E': 'e',
    'SW': 'sw', 'S': 's', 'SE': 'se'
}

# 黏附方向常量
STICKY_DIRECTIONS = {
    'N': 'n', 'S': 's', 'E': 'e', 'W': 'w',
    'NS': 'ns', 'EW': 'ew', 'NSEW': 'nsew'
}

# 語言常量
SUPPORTED_LANGUAGES = {
    'EN': 'en',
    'ZH_TW': 'zh-TW',
    'ZH_CN': 'zh-CN'
}

# 默認語言
DEFAULT_LANGUAGE = SUPPORTED_LANGUAGES['ZH_TW']

# 顏色常量
DEFAULT_COLORS = {
    'PRIMARY_BG': '#3498db',
    'SECONDARY_BG': '#2c3e50',
    'SUCCESS_BG': '#27ae60',
    'WARNING_BG': '#f39c12',
    'ERROR_BG': '#e74c3c',
    'INFO_BG': '#17a2b8',
    'LIGHT_BG': '#ecf0f1',
    'DARK_BG': '#2c3e50',
    'WHITE': '#ffffff',
    'BLACK': '#000000',
    'GRAY': '#6c757d'
}

# 字體常量
DEFAULT_FONTS = {
    'PRIMARY': 'Arial,12',
    'SECONDARY': 'Arial,10',
    'HEADER': 'Arial,16,bold',
    'BUTTON': 'Arial,12,bold',
    'SMALL': 'Arial,8'
}

# 樣式屬性常量
STYLE_PROPERTIES = {
    'BACKGROUND': 'bg',
    'FOREGROUND': 'fg',
    'FONT': 'font',
    'BORDER': 'border',
    'RELIEF': 'relief',
    'CURSOR': 'cursor'
}

# API 響應常量
API_RESPONSE_KEYS = {
    'SUCCESS': 'success',
    'ERROR': 'error',
    'MESSAGE': 'message',
    'STATUS_CODE': 'status_code',
    'RESPONSE': 'response',
    'DATA': 'data'
}

# 錯誤消息常量
ERROR_MESSAGES = {
    'API_NOT_FOUND': '未找到API配置: {api_name}',
    'CONTROL_NOT_FOUND': "找不到控件: {control_name}",
    'INVALID_HTTP_METHOD': "不支援的HTTP方法: {method}",
    'INVALID_LANGUAGE': "不支援的語言: {lang_code}",
    'WINDOW_NOT_FOUND': "窗口 {window_id} 不存在",
    'POPUP_NOT_FOUND': "彈出窗口 '{window_id}' 不存在",
    'INVALID_PARAMETERS': "無效的參數: {params}",
    'PARSE_ERROR': "解析錯誤: {error}",
    'NETWORK_ERROR': "網絡錯誤: {error}",
    'TIMEOUT_ERROR': "請求超時: {timeout}s"
}

# 成功消息常量
SUCCESS_MESSAGES = {
    'API_CONNECTED': 'API 已連接',
    'WINDOW_CREATED': '窗口已創建: {window_id}',
    'POPUP_CREATED': '彈出窗口已創建: {window_id}',
    'POPUP_CLOSED': '彈出窗口已關閉: {window_id}',
    'CONFIGURATION_UPDATED': '配置已更新: {config_name}',
    'LANGUAGE_SET': '語言已設定為: {lang_code}',
    'ADAPTIVE_LAYOUT_ENABLED': '自適應佈局已啟用'
}

# 警告消息常量
WARNING_MESSAGES = {
    'CONTROL_NOT_FOUND_FOR_POSITIONING': "警告: 控件 '{ctrl_name}' 未找到，無法設定相對位置",
    'CONTROL_NOT_FOUND_FOR_GRID': "警告: 控件 '{ctrl_name}' 未找到，無法設定網格位置",
    'INVALID_SIZE_FORMAT': "警告: 無效的尺寸格式，使用默認值",
    'FRAMELESS_MODE_UNAVAILABLE': "警告: 無邊框模式在此平台上不可用",
    'SYSTEM_BUTTONS_REMOVAL_FAILED': "警告: 無法移除系統按鈕"
}

# 文件路徑常量
PATHS = {
    'CONFIG_DIR': 'config',
    'EXAMPLES_DIR': 'examples',
    'PLUGINS_DIR': 'plugins',
    'LOGS_DIR': 'logs'
}

# 日誌級別常量
LOG_LEVELS = {
    'DEBUG': 'DEBUG',
    'INFO': 'INFO',
    'WARNING': 'WARNING',
    'ERROR': 'ERROR',
    'CRITICAL': 'CRITICAL'
}

# 配置文件名常量
CONFIG_FILES = {
    'DEFAULT_CONFIG': 'default_config.json',
    'USER_CONFIG': 'user_config.json',
    'PLUGIN_CONFIG': 'plugin_config.json'
}

# 指令別名映射
COMMAND_ALIASES = {
    "win": "window",
    "ctrl": "control",
    "api-set": "API設定",
    "api-call": "API呼叫",
    "api": "API設定",
    "api-preset": "API預設",
    "api-call-preset": "API呼叫預設",
    "display-area": "顯示區域",
    "display-content": "顯示內容",
    "display-text": "顯示文字",
    "set-language": "設定語言",
    "generate-code": "生成代碼",
    "clear-display": "清除顯示",
    "adaptive": "自適應",
    "relative": "相對位置",
    "grid-setup": "網格佈局",
    "grid-pos": "網格位置",
    "layout-grid": "LayoutGrid",
    "grid-layout": "網格佈局",
}

# 彈出窗口指令集合
POPUP_COMMANDS = {
    'popup-window',
    'popup-content',
    'popup-send-data'
}

# 處理順序定義
PROCESSING_ORDER = [
    'clear',           # 清除
    'window',          # 窗口
    'style',           # 樣式
    'control',         # 控件
    'grid-setup',      # 網格設置
    'layout-grid',     # 佈局網格
    'binding',         # 綁定
    'api-set',         # API設置
    'api-call',        # API呼叫
    'popup-window',    # 彈出窗口
    'popup-content',   # 彈出內容
    'popup-send-data', # 彈出數據傳送
    'show'             # 顯示
]