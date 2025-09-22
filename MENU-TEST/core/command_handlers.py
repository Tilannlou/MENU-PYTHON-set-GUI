"""
指令处理器集合模块
包含所有MENU002指令的处理器实现
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import threading
from typing import Any, Dict, List, Optional, Tuple

from utils.logger import logger
from utils.helpers import (
    parse_size_string, parse_parameters, format_string_with_context,
    safe_eval_expression, extract_target_from_args, generate_unique_id
)
from utils.constants import (
    DEFAULT_WINDOW_SIZE, DEFAULT_COLORS, DEFAULT_FONTS,
    ANCHOR_POINTS, STICKY_DIRECTIONS, COMMAND_ALIASES,
    ERROR_MESSAGES, SUCCESS_MESSAGES, WARNING_MESSAGES
)
from .command_registry import registry
from .language_manager import get_text
from .api_manager import api_manager
from .ui_components import DisplayArea, CodeDisplayArea


@registry.register("clear")
def cmd_clear(app, *args):
    """清除所有控件与样式，初始化 scaffold"""
    app.controls.clear()
    app.styles.clear()
    app.exec_map.clear()
    app.binding_list.clear()
    app.display_areas.clear()

    # 清除UI组件
    if hasattr(app, 'status_bar'):
        app.status_bar.set_status(get_text("ready"))
    if hasattr(app, 'toolbar'):
        # 清除工具栏按钮
        for widget in app.toolbar.frame.winfo_children():
            widget.destroy()
        app.toolbar.buttons.clear()
        app.toolbar.callbacks.clear()

    logger.info("清除所有控件和样式")


@registry.register("window")
def cmd_window(app, *args):
    """建立主视窗，设定尺寸与标题"""
    try:
        # 参数数量可变，至少需要4个参数
        if len(args) < 4:
            logger.error("window指令需要至少4个参数: name, width, height, title")
            return
            
        name = args[0]
        width = args[1]
        height = args[2]
        title = ' '.join(args[3:])  # 标题可能包含空格
        
        w, h = parse_size_string(f"{width}x{height}")
        app.root = tk.Tk()
        app.root.title(title)
        app.root.geometry(f"{w}x{h}")

        # 应用窗口样式
        style = app.styles.get(name, {})
        if "bg" in style:
            app.root.config(bg=style["bg"])

        # 创建默认UI组件
        app.status_bar = _create_status_bar(app.root)
        app.toolbar = _create_toolbar(app.root)

        logger.info(f"创建主窗口: {name} ({w}x{h}) - {title}")

    except Exception as e:
        logger.error(f"创建窗口失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("style")
def cmd_style(app, class_name: str, *props):
    """定义样式类别，供控件套用"""
    style_dict = parse_parameters(list(props))
    app.styles[class_name] = style_dict
    logger.debug(f"定义样式: {class_name} - {style_dict}")


@registry.register("control")
def cmd_control(app, ctrl_type: str, name: str, *props):
    """建立 UI 控件（Label, Button, Entry）"""
    try:
        params = parse_parameters(list(props))

        # 解析位置和尺寸
        x = int(params.get("x", 0))
        y = int(params.get("y", 0))
        w = int(params.get("w", 0)) if "w" in params else None
        h = int(params.get("h", 0)) if "h" in params else None

        # 获取样式
        cls = params.get("class")
        style = app.styles.get(cls, {}) if cls else {}

        # 创建控件
        widget = _create_widget(app.root, ctrl_type, params, style)

        # 设置位置
        if hasattr(app, "grid_cfg") and "row" in params:
            _place_widget_grid(widget, params)
        else:
            _place_widget_absolute(widget, x, y, w, h, params)

        # 存储控件引用
        app.controls[name] = widget

        # 处理相对位置
        if "relx" in params:
            _apply_relative_positioning(widget, params)

        logger.debug(f"创建控件: {name} ({ctrl_type})")

    except Exception as e:
        logger.error(f"创建控件失败: {name} - {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("grid-setup")
def cmd_grid_setup(app, rows: str, cols: str, row_weight: str = None, col_weight: str = None):
    """设定响应式网格布局的行列与权重"""
    try:
        rows_int = int(rows)
        cols_int = int(cols)

        app.grid_cfg = {
            "rows": rows_int,
            "cols": cols_int,
            "pad": 5  # 默认内边距
        }

        # 设定权重
        if row_weight:
            weights = [int(w) for w in row_weight.split(",")]
            for i, weight in enumerate(weights):
                if i < rows_int:
                    app.root.grid_rowconfigure(i, weight=weight)

        if col_weight:
            weights = [int(w) for w in col_weight.split(",")]
            for i, weight in enumerate(weights):
                if i < cols_int:
                    app.root.grid_columnconfigure(i, weight=weight)

        logger.debug(f"设定网格布局: {rows_int}x{cols_int}")

    except Exception as e:
        logger.error(f"网格布局设定失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("layout-grid")
def cmd_layout_grid(app, rows: str, cols: str):
    """启用网格布局模式"""
    try:
        rows_int = int(rows)
        cols_int = int(cols)

        # 设定网格配置
        for i in range(rows_int):
            app.root.grid_rowconfigure(i, weight=1)
        for j in range(cols_int):
            app.root.grid_columnconfigure(j, weight=1)

        logger.debug(f"启用网格布局: {rows_int}x{cols_int}")

    except Exception as e:
        logger.error(f"网格布局启用失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("grid-pos")
def cmd_grid_position(app, ctrl_name: str, row: str, col: str,
                     rowspan: str = "1", colspan: str = "1",
                     sticky: str = "nsew"):
    """在网格中定位控件"""
    try:
        widget = app.controls.get(ctrl_name)
        if not widget:
            logger.warning(WARNING_MESSAGES['CONTROL_NOT_FOUND_FOR_GRID'].format(ctrl_name=ctrl_name))
            return

        widget.grid(
            row=int(row),
            column=int(col),
            rowspan=int(rowspan),
            columnspan=int(colspan),
            sticky=sticky
        )

        logger.debug(f"网格定位: {ctrl_name} -> ({row},{col})")

    except Exception as e:
        logger.error(f"网格定位失败: {ctrl_name} - {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("relative")
def cmd_relative_position(app, ctrl_name: str, relx: str = None,
                         rely: str = None, relwidth: str = None,
                         relheight: str = None, anchor: str = "nw"):
    """设定相对位置"""
    try:
        widget = app.controls.get(ctrl_name)
        if not widget:
            logger.warning(WARNING_MESSAGES['CONTROL_NOT_FOUND_FOR_POSITIONING'].format(ctrl_name=ctrl_name))
            return

        place_args = {"anchor": anchor}
        if relx:
            place_args["relx"] = float(relx)
        if rely:
            place_args["rely"] = float(rely)
        if relwidth:
            place_args["relwidth"] = float(relwidth)
        if relheight:
            place_args["relheight"] = float(relheight)

        widget.place(**place_args)
        logger.debug(f"相对定位: {ctrl_name}")

    except Exception as e:
        logger.error(f"相对定位失败: {ctrl_name} - {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("binding")
def cmd_binding(app, *args):
    """绑定控件事件与表达式更新"""
    try:
        # 参数数量可变，至少需要3个参数
        if len(args) < 3:
            logger.error("binding指令需要至少3个参数: widget_name, event, action")
            return
            
        widget_name = args[0]
        event = args[1]
        action = ' '.join(args[2:])  # 动作可能包含空格

        app.binding_list.append((widget_name, event, action))
        logger.debug(f"绑定事件: {widget_name}.{event} -> {action}")

    except Exception as e:
        logger.error(f"事件绑定失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("exec")
def cmd_exec(app, button_name: str, *commands):
    """绑定按钮执行命令"""
    try:
        if button_name not in app.exec_map:
            app.exec_map[button_name] = []

        app.exec_map[button_name].extend(commands)
        logger.debug(f"绑定执行命令: {button_name} -> {commands}")

    except Exception as e:
        logger.error(f"执行命令绑定失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("API設定")
def handle_api_setup(app, api_name: str, url: str, *args):
    """处理API设定指令"""
    try:
        params = parse_parameters(list(args))

        # 解析参数
        key = params.get('key')
        username = params.get('username')
        password = params.get('password')
        show_secret = params.get('show-secret', 'false').lower() in ('true', '1', 'yes')

        # 添加到API管理器
        success = api_manager.add_api(api_name, url, key, username, password, show_secret)

        if success:
            logger.info(f"API设定成功: {api_name}")
        else:
            logger.error(f"API设定失败: {api_name}")

    except Exception as e:
        logger.error(f"API设定处理失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("API呼叫")
def handle_api_call(app, btn_name: str, api_name: str, method: str, path: str, *args):
    """处理API呼叫指令"""
    try:
        # 解析参数
        remaining_args, target = extract_target_from_args(list(args))
        data_template = ' '.join(remaining_args) if remaining_args else None

        # 获取按钮控件
        btn = app.controls.get(btn_name)
        if not btn:
            logger.warning(f"找不到按钮: {btn_name}")
            return

        def on_click():
            try:
                # 准备上下文数据
                ctx = {name: widget.get() for name, widget in app.controls.items()
                       if hasattr(widget, 'get')}

                # 在后台线程中执行API呼叫
                def call_api_task():
                    try:
                        result = api_manager.call_api(api_name, method, path, data_template, ctx)

                        # 更新UI（需要在主线程中执行）
                        def update_ui():
                            if target:
                                _update_target_widget(app, target, result)
                            else:
                                # 显示结果
                                messagebox.showinfo("API结果", str(result))

                        app.root.after(0, update_ui)

                    except Exception as e:
                        def show_error():
                            messagebox.showerror("API错误", str(e))
                        app.root.after(0, show_error)

                threading.Thread(target=call_api_task, daemon=True).start()

            except Exception as e:
                messagebox.showerror("错误", str(e))

        # 绑定点击事件
        if hasattr(btn, 'config'):
            btn.config(command=on_click)
        else:
            btn.bind('<Button-1>', lambda e: on_click())

        logger.debug(f"绑定API呼叫: {btn_name} -> {api_name} {method} {path}")

    except Exception as e:
        logger.error(f"API呼叫处理失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("顯示區域")
def cmd_display_area(app, area_name: str, x: str, y: str, width: str, height: str, *props):
    """创建或配置显示区域"""
    try:
        params = parse_parameters(list(props))

        # 创建显示区域
        display_area = DisplayArea(
            app.root,
            area_name,
            int(x), int(y),
            int(width), int(height),
            params
        )

        app.display_areas[area_name] = display_area
        logger.debug(f"创建显示区域: {area_name}")

    except Exception as e:
        logger.error(f"显示区域创建失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("顯示內容")
def cmd_display_content(app, area_name: str, content: str, *props):
    """在指定显示区域显示内容"""
    try:
        if area_name not in app.display_areas:
            logger.warning(f"显示区域不存在: {area_name}")
            return

        display_area = app.display_areas[area_name]
        params = parse_parameters(list(props))

        display_area.set_content(content, **params)
        logger.debug(f"更新显示内容: {area_name}")

    except Exception as e:
        logger.error(f"显示内容更新失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("清除顯示")
def cmd_clear_display(app, area_name: str):
    """清除指定显示区域的内容"""
    try:
        if area_name not in app.display_areas:
            logger.warning(f"显示区域不存在: {area_name}")
            return

        app.display_areas[area_name].clear_content()
        logger.debug(f"清除显示区域: {area_name}")

    except Exception as e:
        logger.error(f"显示区域清除失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("設定語言")
def cmd_set_language(app, lang_code: str):
    """设定界面语言"""
    try:
        if hasattr(app, 'language'):
            success = app.language.set_language(lang_code)
            if success:
                logger.info(f"语言设定成功: {lang_code}")
            else:
                logger.warning(f"语言设定失败: {lang_code}")
        else:
            logger.warning("语言管理器未初始化")

    except Exception as e:
        logger.error(f"语言设定失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("顯示文字")
def cmd_display_text(app, key: str, target: str, *props):
    """显示多语言文字"""
    try:
        text = get_text(key)

        # 检查目标是否是显示区域
        if target in app.display_areas:
            display_area = app.display_areas[target]
            params = parse_parameters(list(props))
            display_area.set_content(text, **params)
        else:
            # 在控件上显示文字
            widget = app.controls.get(target)
            if widget:
                if hasattr(widget, 'config'):
                    widget.config(text=text)
                elif hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                    widget.delete(0, 'end')
                    widget.insert(0, text)

        logger.debug(f"显示多语言文字: {key} -> {target}")

    except Exception as e:
        logger.error(f"多语言文字显示失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("生成代碼")
def cmd_generate_code(app, target: str = None):
    """生成并显示对应的 Python 代码"""
    try:
        # 生成代码
        code_lines = _generate_python_code(app)

        if target and target in app.display_areas:
            # 在显示区域显示代码
            display_area = app.display_areas[target]
            display_area.set_code_content('\n'.join(code_lines), 'python')
        else:
            # 创建新窗口显示代码
            _show_code_in_window(app, '\n'.join(code_lines))

        logger.debug("代码生成完成")

    except Exception as e:
        logger.error(f"代码生成失败: {e}")
        # 不抛出异常，继续执行其他指令


@registry.register("執行指令")
def cmd_execute_single_command(app, command_text: str = None):
    """执行单个MENU指令"""
    try:
        if not command_text:
            # 从输入框获取指令
            command_input = app.get_control("command_input")
            if command_input:
                command_text = command_input.get()
            else:
                app.show_message("错误", "找不到指令输入框")
                return

        if not command_text.strip():
            app.show_message("提示", "请输入要执行的指令")
            return

        # 解析指令
        tokens = parse_command_line(command_text)
        if not tokens:
            app.show_message("错误", "无效的指令格式")
            return

        cmd = tokens[0].lower()
        args = tokens[1:]

        # 检查指令是否存在
        handler = registry.get(cmd)
        if not handler:
            app.show_message("错误", f"未知指令: {cmd}")
            return

        # 执行指令
        result = handler(app, *args)

        # 显示结果
        result_text = f"✅ 指令执行成功: {command_text}\n"
        if result:
            result_text += f"返回结果: {result}\n"

        result_area = app.get_display_area("result_area")
        if result_area:
            current_content = result_area.get_content()
            result_area.set_content(current_content + "\n" + result_text)

        logger.info(f"单个指令执行成功: {command_text}")

    except Exception as e:
        error_text = f"❌ 指令执行失败: {command_text}\n错误: {str(e)}\n"
        result_area = app.get_display_area("result_area")
        if result_area:
            current_content = result_area.get_content()
            result_area.set_content(current_content + "\n" + error_text)

        logger.error(f"单个指令执行失败: {e}")
        app.show_message("执行错误", str(e))


# 其他函数保持不变...

# 导入必要的模块
from utils.helpers import parse_command_line


# 导入必要的模块
from datetime import datetime


# 辅助函数
def _create_widget(parent: tk.Widget, ctrl_type: str, params: Dict[str, str],
                  style: Dict[str, str]) -> tk.Widget:
    """创建控件"""
    text = params.get("text", "")
    ctrl_type = ctrl_type.lower()

    if ctrl_type == "button":
        widget = tk.Button(parent, text=text)
    elif ctrl_type in ("entry", "edit"):
        widget = tk.Entry(parent)
        placeholder = params.get("placeholder")
        if placeholder:
            widget.insert(0, placeholder)
    elif ctrl_type in ("label", "text"):
        widget = tk.Label(parent, text=text)
    else:
        widget = tk.Label(parent, text=text)

    # 应用样式
    if "bg" in style:
        widget.config(bg=style["bg"])
    if "color" in style:
        widget.config(fg=style["color"])
    if "font" in style:
        widget.config(font=tuple(style["font"].split(",")))

    return widget


def _place_widget_absolute(widget: tk.Widget, x: int, y: int, w: int, h: int,
                          params: Dict[str, str]):
    """绝对位置放置控件"""
    place_kwargs = {"x": x, "y": y}
    if w and h:
        place_kwargs["width"] = w
        place_kwargs["height"] = h
    widget.place(**place_kwargs)


def _place_widget_grid(widget: tk.Widget, params: Dict[str, str]):
    """网格位置放置控件"""
    widget.grid(
        row=int(params["row"]),
        column=int(params["col"]),
        rowspan=int(params.get("rowspan", 1)),
        columnspan=int(params.get("colspan", 1)),
        sticky=params.get("sticky", "")
    )


def _apply_relative_positioning(widget: tk.Widget, params: Dict[str, str]):
    """应用相对位置"""
    place_args = {}
    if "relx" in params:
        place_args["relx"] = float(params["relx"])
    if "rely" in params:
        place_args["rely"] = float(params["rely"])
    if "relwidth" in params:
        place_args["relwidth"] = float(params["relwidth"])
    if "relheight" in params:
        place_args["relheight"] = float(params["relheight"])
    if "anchor" in params:
        place_args["anchor"] = params["anchor"]

    if place_args:
        widget.place(**place_args)


def _update_target_widget(app, target: str, result: Any):
    """更新目标控件"""
    if '.' in target:
        widget_name, attr = target.split('.', 1)
        widget = app.controls.get(widget_name)
        if widget:
            if attr == 'text' and hasattr(widget, 'config'):
                widget.config(text=str(result))
            elif attr == 'value' and hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                widget.delete(0, 'end')
                widget.insert(0, str(result))
            elif attr == 'content' and hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                widget.config(state="normal")
                widget.delete(1.0, "end")
                widget.insert("end", str(result))
                widget.config(state="disabled")
    else:
        # 存储到应用变量
        setattr(app, target, result)


def _generate_python_code(app) -> List[str]:
    """生成Python代码"""
    code_lines = ["# MENU002 生成的代码"]
    code_lines.append("import tkinter as tk")
    code_lines.append("")
    code_lines.append("class GeneratedApp:")
    code_lines.append("    def __init__(self):")
    code_lines.append("        self.root = tk.Tk()")
    if app.root:
        code_lines.append(f"        self.root.title('{app.root.title()}')")
        code_lines.append(f"        self.root.geometry('{app.root.winfo_width()}x{app.root.winfo_height()}')")
    else:
        code_lines.append("        self.root.title('Generated App')")
        code_lines.append("        self.root.geometry('800x600')")
    code_lines.append("        self.controls = {}")
    code_lines.append("")

    # 添加控件创建代码
    for name, widget in app.controls.items():
        if isinstance(widget, tk.Button):
            code_lines.append(f"        self.controls['{name}'] = tk.Button(self.root, text='{widget.cget('text')}')")
        elif isinstance(widget, tk.Label):
            code_lines.append(f"        self.controls['{name}'] = tk.Label(self.root, text='{widget.cget('text')}')")
        elif isinstance(widget, tk.Entry):
            code_lines.append(f"        self.controls['{name}'] = tk.Entry(self.root)")

        # 添加位置信息
        geometry = widget.winfo_geometry()
        code_lines.append(f"        self.controls['{name}'].place({geometry})")
        code_lines.append("")

    code_lines.append("    def run(self):")
    code_lines.append("        self.root.mainloop()")
    code_lines.append("")
    code_lines.append("if __name__ == '__main__':")
    code_lines.append("    app = GeneratedApp()")
    code_lines.append("    app.run()")

    return code_lines


def _show_code_in_window(app, code: str):
    """在新窗口中显示代码"""
    code_window = tk.Toplevel(app.root if app.root else tk.Tk())
    code_window.title("生成的代码")
    code_window.geometry("800x600")

    code_text = scrolledtext.ScrolledText(code_window, wrap=tk.WORD)
    code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    code_text.insert(tk.END, code)
    code_text.config(state=tk.DISABLED)


def _create_status_bar(parent: tk.Widget):
    """创建状态栏"""
    from .ui_components import StatusBar
    return StatusBar(parent)


def _create_toolbar(parent: tk.Widget):
    """创建工具栏"""
    from .ui_components import ToolBar

    buttons = [
        {"name": "clear", "text": "清除", "command": None},
        {"name": "test", "text": "测试", "command": None},
        {"name": "generate", "text": "生成代码", "command": None}
    ]

    return ToolBar(parent, buttons)