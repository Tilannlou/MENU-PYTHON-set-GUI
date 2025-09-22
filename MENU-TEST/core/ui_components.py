"""
UI組件模塊
提供通用的UI組件和佈局工具
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from utils.logger import logger
from utils.constants import DEFAULT_COLORS, DEFAULT_FONTS, ANCHOR_POINTS, STICKY_DIRECTIONS


class DisplayArea:
    """
    顯示區域組件
    提供可配置的文本顯示區域
    """

    def __init__(self, parent: tk.Widget, name: str, x: int, y: int,
                 width: int, height: int, config: Dict[str, Any] = None):
        """
        初始化顯示區域

        Args:
            parent: 父容器
            name: 區域名稱
            x, y: 位置
            width, height: 尺寸
            config: 配置參數
        """
        self.name = name
        self.config = config or {}

        # 創建框架
        self.frame = tk.Frame(
            parent,
            bg=self.config.get('bg', DEFAULT_COLORS['LIGHT_BG'])
        )
        self.frame.place(x=x, y=y, width=width, height=height)

        # 添加標題
        if 'title' in self.config:
            self.title_label = tk.Label(
                self.frame,
                text=self.config['title'],
                bg=self.config.get('bg', DEFAULT_COLORS['LIGHT_BG']),
                fg=self.config.get('color', DEFAULT_COLORS['BLACK']),
                font=self.config.get('font', DEFAULT_FONTS['HEADER'])
            )
            self.title_label.pack(pady=5)

        # 創建文本區域
        self.text_widget = tk.Text(
            self.frame,
            wrap='word',
            bg=self.config.get('content_bg', DEFAULT_COLORS['LIGHT_BG']),
            fg=self.config.get('content_color', DEFAULT_COLORS['BLACK']),
            font=self.config.get('content_font', DEFAULT_FONTS['PRIMARY']),
            state='disabled'
        )
        self.text_widget.pack(fill='both', expand=True, padx=5, pady=5)

        logger.debug(f"創建顯示區域: {name} ({width}x{height})")

    def set_content(self, content: str, **styles):
        """
        設置顯示內容

        Args:
            content: 要顯示的內容
            **styles: 樣式參數
        """
        # 處理 None 值
        if content is None:
            content = "❌ 表達式評估失敗"

        # 確保內容是字符串類型
        if not isinstance(content, str):
            content = str(content)

        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, 'end')
        self.text_widget.insert('end', content)

        # 應用樣式
        if 'color' in styles:
            self.text_widget.config(fg=styles['color'])
        if 'font' in styles:
            self.text_widget.config(font=styles['font'])
        if 'size' in styles:
            current_font = self.text_widget.cget('font')
            font_name = current_font[0] if isinstance(current_font, tuple) else 'Arial'
            self.text_widget.config(font=(font_name, int(styles['size'])))

        self.text_widget.config(state='disabled')
        logger.debug(f"更新顯示區域內容: {self.name}")

    def append_content(self, content: str, **styles):
        """
        追加顯示內容

        Args:
            content: 要追加的內容
            **styles: 樣式參數
        """
        self.text_widget.config(state='normal')
        self.text_widget.insert('end', content)

        # 應用樣式
        if styles:
            # 記住當前插入位置
            insert_pos = self.text_widget.index('end-1c')
            for key, value in styles.items():
                if key == 'color':
                    self.text_widget.tag_add('color_tag', insert_pos, 'end')
                    self.text_widget.tag_config('color_tag', foreground=value)
                elif key == 'font':
                    self.text_widget.tag_add('font_tag', insert_pos, 'end')
                    self.text_widget.tag_config('font_tag', font=value)

        self.text_widget.config(state='disabled')

    def clear_content(self):
        """清除顯示內容"""
        self.text_widget.config(state='normal')
        self.text_widget.delete(1.0, 'end')
        self.text_widget.config(state='disabled')
        logger.debug(f"清除顯示區域內容: {self.name}")

    def get_content(self) -> str:
        """
        獲取顯示內容

        Returns:
            顯示的內容
        """
        return self.text_widget.get(1.0, 'end-1c')

    def set_title(self, title: str):
        """
        設置標題

        Args:
            title: 標題文字
        """
        if hasattr(self, 'title_label'):
            self.title_label.config(text=title)
        else:
            # 創建標題標籤
            self.title_label = tk.Label(
                self.frame,
                text=title,
                bg=self.config.get('bg', DEFAULT_COLORS['LIGHT_BG']),
                fg=self.config.get('color', DEFAULT_COLORS['BLACK']),
                font=self.config.get('font', DEFAULT_FONTS['HEADER'])
            )
            self.title_label.pack(pady=5)

    def update_config(self, config: Dict[str, Any]):
        """
        更新配置

        Args:
            config: 新的配置
        """
        self.config.update(config)

        # 更新框架樣式
        if 'bg' in config:
            self.frame.config(bg=config['bg'])

        # 更新文本區域樣式
        if 'content_bg' in config:
            self.text_widget.config(bg=config['content_bg'])
        if 'content_color' in config:
            self.text_widget.config(fg=config['content_color'])
        if 'content_font' in config:
            self.text_widget.config(font=config['content_font'])

        logger.debug(f"更新顯示區域配置: {self.name}")


class CodeDisplayArea(DisplayArea):
    """
    代碼顯示區域
    專門用於顯示代碼的顯示區域
    """

    def __init__(self, parent: tk.Widget, name: str, x: int, y: int,
                 width: int, height: int, config: Dict[str, Any] = None):
        """
        初始化代碼顯示區域

        Args:
            parent: 父容器
            name: 區域名稱
            x, y: 位置
            width, height: 尺寸
            config: 配置參數
        """
        # 設置代碼顯示默認配置
        code_config = {
            'content_bg': '#f8f9fa',
            'content_font': 'Consolas,10' if 'Consolas' in str(tk.font.families()) else 'Courier,10',
            'line_numbers': True,
            'syntax_highlight': False
        }
        code_config.update(config or {})

        super().__init__(parent, name, x, y, width, height, code_config)

    def set_code_content(self, code: str, language: str = 'python'):
        """
        設置代碼內容

        Args:
            code: 代碼內容
            language: 代碼語言
        """
        self.set_content(code)

        # 這裡可以添加語法高亮功能
        if self.config.get('syntax_highlight', False):
            self._apply_syntax_highlight(language)

    def _apply_syntax_highlight(self, language: str):
        """
        應用語法高亮

        Args:
            language: 代碼語言
        """
        # 簡單的語法高亮實現
        # 這裡可以擴展為更完整的語法高亮
        try:
            # 關鍵字高亮
            keywords = ['def', 'class', 'if', 'else', 'for', 'while', 'import', 'from', 'return']
            for keyword in keywords:
                start_pos = '1.0'
                while True:
                    start_pos = self.text_widget.search(keyword, start_pos, 'end')
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(keyword)}c"
                    self.text_widget.tag_add('keyword', start_pos, end_pos)
                    start_pos = end_pos

            # 配置關鍵字標籤
            self.text_widget.tag_config('keyword', foreground='blue', font='bold')

        except Exception as e:
            logger.warning(f"語法高亮應用失敗: {e}")


class StatusBar:
    """
    狀態欄組件
    提供狀態信息顯示
    """

    def __init__(self, parent: tk.Widget, height: int = 25):
        """
        初始化狀態欄

        Args:
            parent: 父容器
            height: 狀態欄高度
        """
        self.parent = parent
        self.height = height

        # 創建狀態欄框架
        self.frame = tk.Frame(
            parent,
            bg=DEFAULT_COLORS['SECONDARY_BG'],
            height=height
        )
        self.frame.pack(side='bottom', fill='x')
        self.frame.pack_propagate(False)

        # 創建狀態標籤
        self.status_label = tk.Label(
            self.frame,
            text="就緒",
            bg=DEFAULT_COLORS['SECONDARY_BG'],
            fg=DEFAULT_COLORS['WHITE'],
            font=DEFAULT_FONTS['SMALL'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=5, pady=2)

        # 創建進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame,
            variable=self.progress_var,
            style='TProgressbar'
        )
        self.progress_bar.pack(side='right', padx=5, pady=2, fill='x', expand=True)

        logger.debug("創建狀態欄")

    def set_status(self, message: str, status_type: str = 'info'):
        """
        設置狀態信息

        Args:
            message: 狀態消息
            status_type: 狀態類型 (info, success, warning, error)
        """
        self.status_label.config(text=message)

        # 根據狀態類型設置顏色
        colors = {
            'info': DEFAULT_COLORS['WHITE'],
            'success': DEFAULT_COLORS['SUCCESS_BG'],
            'warning': DEFAULT_COLORS['WARNING_BG'],
            'error': DEFAULT_COLORS['ERROR_BG']
        }

        color = colors.get(status_type, DEFAULT_COLORS['WHITE'])
        self.status_label.config(fg=color)

        logger.debug(f"狀態更新: {message} ({status_type})")

    def set_progress(self, value: float, maximum: float = 100.0):
        """
        設置進度條

        Args:
            value: 當前值
            maximum: 最大值
        """
        if maximum > 0:
            progress = (value / maximum) * 100
            self.progress_var.set(progress)

    def clear_progress(self):
        """清除進度條"""
        self.progress_var.set(0)

    def show_progress_indeterminate(self):
        """顯示不確定進度"""
        self.progress_bar.config(mode='indeterminate')
        self.progress_bar.start()

    def stop_progress_indeterminate(self):
        """停止不確定進度"""
        self.progress_bar.stop()
        self.progress_bar.config(mode='determinate')


class ToolBar:
    """
    工具欄組件
    提供按鈕工具欄
    """

    def __init__(self, parent: tk.Widget, buttons: List[Dict[str, Any]] = None):
        """
        初始化工具欄

        Args:
            parent: 父容器
            buttons: 按鈕配置列表
        """
        self.parent = parent
        self.buttons = []
        self.callbacks = {}

        # 創建工具欄框架
        self.frame = tk.Frame(
            parent,
            bg=DEFAULT_COLORS['LIGHT_BG'],
            height=40
        )
        self.frame.pack(side='top', fill='x')
        self.frame.pack_propagate(False)

        # 創建按鈕
        if buttons:
            self.add_buttons(buttons)

        logger.debug("創建工具欄")

    def add_button(self, name: str, text: str, command: Callable = None,
                  icon: str = None, tooltip: str = None) -> tk.Button:
        """
        添加工具欄按鈕

        Args:
            name: 按鈕名稱
            text: 按鈕文字
            command: 點擊回調
            icon: 圖標
            tooltip: 提示文字

        Returns:
            創建的按鈕
        """
        button = tk.Button(
            self.frame,
            text=text,
            command=command,
            bg=DEFAULT_COLORS['PRIMARY_BG'],
            fg=DEFAULT_COLORS['WHITE'],
            font=DEFAULT_FONTS['BUTTON'],
            relief='flat'
        )

        button.pack(side='left', padx=2, pady=5)
        self.buttons.append(button)
        self.callbacks[name] = command

        if tooltip:
            self._add_tooltip(button, tooltip)

        logger.debug(f"添加工具欄按鈕: {name}")
        return button

    def add_buttons(self, buttons: List[Dict[str, Any]]):
        """
        批量添加按鈕

        Args:
            buttons: 按鈕配置列表
        """
        for button_config in buttons:
            self.add_button(**button_config)

    def enable_button(self, name: str):
        """
        啟用按鈕

        Args:
            name: 按鈕名稱
        """
        for button in self.buttons:
            if button.cget('text') == name or hasattr(button, 'name'):
                button.config(state='normal')
                break

    def disable_button(self, name: str):
        """
        禁用按鈕

        Args:
            name: 按鈕名稱
        """
        for button in self.buttons:
            if button.cget('text') == name or hasattr(button, 'name'):
                button.config(state='disabled')
                break

    def _add_tooltip(self, widget: tk.Widget, text: str):
        """
        添加提示文字

        Args:
            widget: 目標控件
            text: 提示文字
        """
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                bg=DEFAULT_COLORS['DARK_BG'],
                fg=DEFAULT_COLORS['WHITE'],
                font=DEFAULT_FONTS['SMALL'],
                relief='solid',
                borderwidth=1
            )
            label.pack()

            def hide_tooltip():
                tooltip.destroy()

            widget.tooltip = tooltip
            widget.bind('<Leave>', lambda e: hide_tooltip())

        widget.bind('<Enter>', show_tooltip)


class MenuBar:
    """
    菜單欄組件
    提供應用程序菜單
    """

    def __init__(self, parent: tk.Widget):
        """
        初始化菜單欄

        Args:
            parent: 父容器
        """
        self.parent = parent
        self.menus = {}

        # 創建主菜單
        self.menubar = tk.Menu(parent)
        parent.config(menu=self.menubar)

        logger.debug("創建菜單欄")

    def add_menu(self, name: str, label: str) -> tk.Menu:
        """
        添加菜單

        Args:
            name: 菜單名稱
            label: 菜單標籤

        Returns:
            菜單對象
        """
        menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=label, menu=menu)
        self.menus[name] = menu

        logger.debug(f"添加菜單: {name}")
        return menu

    def add_menu_item(self, menu_name: str, label: str, command: Callable = None,
                     accelerator: str = None, state: str = 'normal'):
        """
        添加菜單項

        Args:
            menu_name: 菜單名稱
            label: 標籤
            command: 命令回調
            accelerator: 快捷鍵
            state: 狀態
        """
        if menu_name in self.menus:
            self.menus[menu_name].add_command(
                label=label,
                command=command,
                accelerator=accelerator,
                state=state
            )
            logger.debug(f"添加菜單項: {menu_name}.{label}")

    def add_separator(self, menu_name: str):
        """
        添加分隔線

        Args:
            menu_name: 菜單名稱
        """
        if menu_name in self.menus:
            self.menus[menu_name].add_separator()
            logger.debug(f"添加分隔線: {menu_name}")


def create_display_area(parent: tk.Widget, name: str, x: int, y: int,
                       width: int, height: int, **config) -> DisplayArea:
    """
    創建顯示區域的便捷函數

    Args:
        parent: 父容器
        name: 區域名稱
        x, y: 位置
        width, height: 尺寸
        **config: 配置參數

    Returns:
        顯示區域實例
    """
    return DisplayArea(parent, name, x, y, width, height, config)


def create_code_display_area(parent: tk.Widget, name: str, x: int, y: int,
                           width: int, height: int, **config) -> CodeDisplayArea:
    """
    創建代碼顯示區域的便捷函數

    Args:
        parent: 父容器
        name: 區域名稱
        x, y: 位置
        width, height: 尺寸
        **config: 配置參數

    Returns:
        代碼顯示區域實例
    """
    return CodeDisplayArea(parent, name, x, y, width, height, config)


def create_status_bar(parent: tk.Widget, **config) -> StatusBar:
    """
    創建狀態欄的便捷函數

    Args:
        parent: 父容器
        **config: 配置參數

    Returns:
        狀態欄實例
    """
    height = config.get('height', 25)
    return StatusBar(parent, height)


def create_toolbar(parent: tk.Widget, buttons: List[Dict[str, Any]] = None) -> ToolBar:
    """
    創建工具欄的便捷函數

    Args:
        parent: 父容器
        buttons: 按鈕配置列表

    Returns:
        工具欄實例
    """
    return ToolBar(parent, buttons)


def create_menubar(parent: tk.Widget) -> MenuBar:
    """
    創建菜單欄的便捷函數

    Args:
        parent: 父容器

    Returns:
        菜單欄實例
    """
    return MenuBar(parent)