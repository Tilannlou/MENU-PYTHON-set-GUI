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
        try:
            app.root = tk.Tk()
            app.root.title(title)
            app.root.geometry(f"{w}x{h}")
        except Exception as tk_error:
            logger.error(f"创建Tkinter窗口失败: {tk_error}")
            logger.warning("GUI环境不可用，跳过窗口创建")
            app.root = None
            return

        # 存儲基準尺寸用於自適應計算
        app._base_width = w
        app._base_height = h

        # 应用窗口样式
        style = app.styles.get(name, {})
        if "bg" in style:
            app.root.config(bg=style["bg"])

        # 创建默认UI组件
        app.status_bar = _create_status_bar(app.root)
        app.toolbar = _create_toolbar(app.root)

        # 绑定窗口大小改变事件以支持响应式布局
        app.root.bind('<Configure>', lambda e: _on_window_resize(app, e))

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

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过控件创建")
            return

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
def cmd_grid_setup(app, *args):
    """设定响应式网格布局的行列与权重"""
    try:
        # 解析参数
        params = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                # 移除引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                params[key] = value

        rows_int = int(params.get('rows', '4'))
        cols_int = int(params.get('cols', '2'))
        row_weight = params.get('row_weight')
        col_weight = params.get('col_weight')

        app.grid_cfg = {
            "rows": rows_int,
            "cols": cols_int,
            "pad": 5  # 默认内边距
        }

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过网格布局设定")
            return

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
def cmd_layout_grid(app, *args):
    """启用网格布局模式"""
    try:
        # 解析参数
        params = {}
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                params[key] = value

        rows_int = int(params.get('rows', '4'))
        cols_int = int(params.get('cols', '2'))

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过网格布局启用")
            return

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


@registry.register("api-set")
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


@registry.register("api-call")
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
                                if app.root:
                                    messagebox.showinfo("API结果", str(result))
                                else:
                                    logger.info(f"API结果: {result}")

                        if app.root:
                            app.root.after(0, update_ui)
                        else:
                            update_ui()

                    except Exception as api_error:
                        # 直接处理错误
                        error_msg = str(api_error)
                        if app.root:
                            app.root.after(0, lambda: messagebox.showerror("API错误", error_msg))
                        else:
                            logger.error(f"API错误: {error_msg}")

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

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过显示区域创建")
            return

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


def _on_window_resize(app, event):
    """
    处理窗口大小改变事件
    重新定位使用相对位置的控件以支持响应式布局
    并自动调整字体大小
    """
    try:
        # 只处理主窗口的大小改变事件
        if event.widget != app.root:
            return

        # 防止過度更新（減少事件觸發頻率）
        current_time = getattr(app, '_last_resize_time', 0)
        import time
        now = time.time()
        if now - current_time < 0.2:  # 200ms 节流，稍微放寬一點
            return
        app._last_resize_time = now

        # 獲取窗口尺寸用於字體自適應計算
        window_width = event.width
        window_height = event.height

        # 基準尺寸（800x600）
        base_width = getattr(app, '_base_width', 800)
        base_height = getattr(app, '_base_height', 600)

        # 計算縮放比例，但限制在合理範圍內
        scale_x = min(window_width / base_width, 1.5)  # 最大放大1.5倍
        scale_y = min(window_height / base_height, 1.5)  # 最大放大1.5倍
        scale = min(scale_x, scale_y, 1.2)  # 總體最大1.2倍，保持適中

        # 重新應用所有使用相對定位的控件
        # 使用更可靠的方法：檢查控件是否有相對定位屬性
        for widget_name, widget in app.controls.items():
            try:
                # 嘗試重新應用相對定位
                place_info = widget.place_info()

                # 檢查是否有相對定位參數
                has_relative = any(key in place_info for key in ['relx', 'rely', 'relwidth', 'relheight'])

                if has_relative:
                    # 創建新的 place 參數，只包含相對定位
                    new_place_args = {}
                    for key in ['relx', 'rely', 'relwidth', 'relheight', 'anchor']:
                        if key in place_info:
                            if key in ['relx', 'rely', 'relwidth', 'relheight']:
                                # 確保數值是浮點數
                                try:
                                    new_place_args[key] = float(place_info[key])
                                except (ValueError, TypeError):
                                    continue
                            else:
                                new_place_args[key] = place_info[key]

                    # 只有當有有效的相對定位參數時才重新應用
                    if new_place_args:
                        widget.place(**new_place_args)
                        logger.debug(f"重新定位控件 {widget_name} 使用參數: {new_place_args}")

                # 自適應字體調整
                if hasattr(widget, 'cget') and hasattr(widget, 'config'):
                    try:
                        current_font = widget.cget('font')
                        if current_font:
                            # 解析當前字體設置
                            if isinstance(current_font, str):
                                # 簡單字體字符串，如 "Arial 12"
                                parts = current_font.split()
                                if len(parts) >= 2:
                                    font_family = parts[0]
                                    try:
                                        base_size = int(parts[1])
                                        # 根據窗口大小調整字體
                                        new_size = max(8, int(base_size * scale))  # 最小8號字
                                        new_font = f"{font_family} {new_size}"
                                        widget.config(font=new_font)
                                    except (ValueError, IndexError):
                                        pass
                            elif isinstance(current_font, tuple) and len(current_font) >= 2:
                                # 字體元組，如 ('Arial', 12, 'bold')
                                font_family = current_font[0]
                                try:
                                    base_size = int(current_font[1])
                                    # 使用更保守的字體縮放：最大放大20%，最小縮小到50%
                                    font_scale = min(max(scale, 0.8), 1.2)
                                    new_size = max(10, min(int(base_size * font_scale), base_size + 4))
                                    new_font = (font_family, new_size) + current_font[2:]
                                    widget.config(font=new_font)
                                except (ValueError, IndexError):
                                    pass
                    except Exception as font_error:
                        logger.debug(f"調整控件 {widget_name} 字體失敗: {font_error}")

            except Exception as widget_error:
                # 單個控件錯誤不應該影響其他控件
                logger.debug(f"重新定位控件 {widget_name} 失敗: {widget_error}")
                continue

        # 調整工作區尺寸（如果有）
        if hasattr(app, 'workspaces'):
            for workspace_name, workspace_frame in app.workspaces.items():
                try:
                    # 檢查工作區是否有相對尺寸設置
                    if hasattr(workspace_frame, '_responsive_config'):
                        config = workspace_frame._responsive_config
                        if 'relwidth' in config and 'relheight' in config:
                            new_width = int(window_width * config['relwidth'])
                            new_height = int(window_height * config['relheight'])
                            workspace_frame.config(width=new_width, height=new_height)
                            logger.debug(f"調整工作區 {workspace_name} 尺寸: {new_width}x{new_height}")
                except Exception as workspace_error:
                    logger.debug(f"調整工作區 {workspace_name} 失敗: {workspace_error}")

        # 更新狀態顯示（如果存在）
        try:
            status_label = app.controls.get('statusLabel')
            if status_label and hasattr(status_label, 'config'):
                status_label.config(text=f"當前窗口大小: {event.width}x{event.height}")
        except Exception as status_error:
            logger.debug(f"更新狀態顯示失敗: {status_error}")

        logger.debug(f"窗口大小改變響應完成: {event.width}x{event.height}, 縮放比例: {scale:.2f}")

    except Exception as e:
        logger.error(f"處理窗口大小改變失敗: {e}")


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
    try:
        if app.root:
            code_window = tk.Toplevel(app.root)
        else:
            code_window = tk.Tk()
        code_window.title("生成的代码")
        code_window.geometry("800x600")

        code_text = scrolledtext.ScrolledText(code_window, wrap=tk.WORD)
        code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        code_text.insert(tk.END, code)
        code_text.config(state=tk.DISABLED)
    except Exception as e:
        logger.error(f"无法显示代码窗口: {e}")
        # 改为记录到日志
        logger.info("生成的代码:")
        for line in code.split('\n'):
            logger.info(line)


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


@registry.register("popup-window")
def cmd_popup_window(app, name: str, title: str, *props):
    """创建弹出窗口"""
    try:
        params = parse_parameters(list(props))

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过弹出窗口创建")
            return

        # 解析尺寸
        size = params.get('size', '400x300')
        if 'x' in size:
            width, height = size.split('x')
            width, height = int(width), int(height)
        else:
            width, height = 400, 300

        # 解析偏移
        offset_x = int(params.get('offset_x', '100'))
        offset_y = int(params.get('offset_y', '100'))

        # 检查是否限制在主窗口内
        constrain_to_parent = params.get('constrain_to_parent', 'true').lower() in ('true', '1', 'yes')

        # 创建弹出窗口
        popup = tk.Toplevel(app.root)
        popup.title(title)

        # 计算窗口位置
        if constrain_to_parent and app.root:
            # 获取主窗口位置和尺寸
            main_x = app.root.winfo_x()
            main_y = app.root.winfo_y()
            main_width = app.root.winfo_width()
            main_height = app.root.winfo_height()

            # 确保popup窗口不会超出主窗口边界
            popup_x = min(max(main_x + offset_x, main_x), main_x + main_width - width)
            popup_y = min(max(main_y + offset_y, main_y), main_y + main_height - height)

            # 如果窗口太大，調整到適合的大小
            if width > main_width:
                width = main_width - 20
            if height > main_height:
                height = main_height - 20
        else:
            # 原始行為：使用絕對偏移
            popup_x = offset_x
            popup_y = offset_y

        popup.geometry(f"{width}x{height}+{popup_x}+{popup_y}")

        # 设置窗口属性
        popup.resizable(True, True)  # 允许调整大小
        popup.transient(app.root)    # 设置为临时窗口（在任务栏中不显示独立图标）

        # 如果限制在父窗口内，绑定移动事件来保持约束
        if constrain_to_parent:
            def constrain_popup_position(event=None):
                try:
                    if popup.winfo_exists() and app.root and app.root.winfo_exists():
                        current_x = popup.winfo_x()
                        current_y = popup.winfo_y()
                        current_width = popup.winfo_width()
                        current_height = popup.winfo_height()

                        main_x = app.root.winfo_x()
                        main_y = app.root.winfo_y()
                        main_width = app.root.winfo_width()
                        main_height = app.root.winfo_height()

                        # 约束位置
                        new_x = max(main_x, min(current_x, main_x + main_width - current_width))
                        new_y = max(main_y, min(current_y, main_y + main_height - current_height))

                        if new_x != current_x or new_y != current_y:
                            popup.geometry(f"{current_width}x{current_height}+{new_x}+{new_y}")
                except:
                    pass  # 忽略位置约束错误

            # 绑定配置事件来检查位置
            popup.bind('<Configure>', constrain_popup_position)

        # 存储弹出窗口引用
        if not hasattr(app, 'popup_windows'):
            app.popup_windows = {}
        app.popup_windows[name] = popup

        logger.debug(f"创建弹出窗口: {name} - {title} (constrained: {constrain_to_parent})")

    except Exception as e:
        logger.error(f"创建弹出窗口失败: {name} - {e}")


@registry.register("popup-content")
def cmd_popup_content(app, popup_name: str, *content_specs):
    """设置弹出窗口内容"""
    try:
        if popup_name not in getattr(app, 'popup_windows', {}):
            logger.warning(f"弹出窗口不存在: {popup_name}")
            return

        popup = app.popup_windows[popup_name]

        # 解析每个内容规格
        for spec in content_specs:
            if spec.startswith('"') and spec.endswith('"'):
                spec = spec[1:-1]  # 移除引号

            # 解析指令
            if spec.startswith('control '):
                # 解析控件指令
                parts = spec.split()
                if len(parts) >= 4:  # control type name prop=value...
                    ctrl_type = parts[1]
                    ctrl_name = parts[2]
                    props_str = ' '.join(parts[3:])

                    # 创建控件参数
                    params = parse_parameters([props_str])

                    # 在弹出窗口中创建控件
                    style = {}  # 简化版，不使用样式
                    widget = _create_widget(popup, ctrl_type, params, style)

                    # 设置位置
                    x = int(params.get("x", 10))
                    y = int(params.get("y", 10))
                    w = int(params.get("w", 0)) if "w" in params else None
                    h = int(params.get("h", 0)) if "h" in params else None

                    _place_widget_absolute(widget, x, y, w, h, params)

                    logger.debug(f"在弹出窗口中创建控件: {ctrl_name}")

    except Exception as e:
        logger.error(f"设置弹出窗口内容失败: {popup_name} - {e}")


@registry.register("popup-send-data")
def cmd_popup_send_data(app, popup_name: str, data: str, target: str):
    """从弹出窗口发送数据到主窗口"""
    try:
        # 更新目标控件
        if '.' in target:
            widget_name, attr = target.split('.', 1)
            widget = app.controls.get(widget_name)
            if widget:
                if attr == 'text' and hasattr(widget, 'config'):
                    widget.config(text=data)
                elif attr == 'value' and hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                    widget.delete(0, 'end')
                    widget.insert(0, data)
        else:
            # 直接在控件上显示
            widget = app.controls.get(target)
            if widget and hasattr(widget, 'config'):
                widget.config(text=data)

        # 关闭弹出窗口
        if popup_name in getattr(app, 'popup_windows', {}):
            app.popup_windows[popup_name].destroy()
            del app.popup_windows[popup_name]
            logger.debug(f"弹出窗口已关闭并发送数据: {popup_name}")

    except Exception as e:
        logger.error(f"发送弹出窗口数据失败: {popup_name} - {e}")


@registry.register("popup-close")
def cmd_popup_close(app, popup_name: str):
    """关闭指定的弹出窗口"""
    try:
        if popup_name in app.popup_windows:
            app.popup_windows[popup_name].destroy()
            del app.popup_windows[popup_name]
            logger.info(f"弹出窗口已关闭: {popup_name}")
        else:
            logger.warning(f"弹出窗口不存在: {popup_name}")
    except Exception as e:
        logger.error(f"关闭弹出窗口失败: {popup_name} - {e}")


@registry.register("popup-list")
def cmd_popup_list(app):
    """列出所有弹出窗口"""
    try:
        if not app.popup_windows:
            app.show_message("弹出窗口列表", "没有打开的弹出窗口")
            return

        popup_info = "当前弹出窗口:\n" + "\n".join(
            f"- {name}: {window.title() if window and window.winfo_exists() else '已销毁'}"
            for name, window in app.popup_windows.items()
        )
        app.show_message("弹出窗口列表", popup_info)
        logger.debug("显示弹出窗口列表")
    except Exception as e:
        logger.error(f"列出弹出窗口失败: {e}")


@registry.register("window-maximize")
def cmd_window_maximize(app, window_name: str):
    """最大化指定窗口"""
    try:
        if window_name == "main" and app.root:
            app.root.state('zoomed')
            logger.info("主窗口已最大化")
        elif window_name in app.popup_windows:
            popup = app.popup_windows[window_name]
            if popup and popup.winfo_exists():
                popup.state('zoomed')
                logger.info(f"弹出窗口已最大化: {window_name}")
            else:
                logger.warning(f"弹出窗口不存在或已销毁: {window_name}")
        else:
            logger.warning(f"窗口不存在: {window_name}")
    except Exception as e:
        logger.error(f"最大化窗口失败: {window_name} - {e}")


@registry.register("window-minimize")
def cmd_window_minimize(app, window_name: str):
    """最小化指定窗口"""
    try:
        if window_name == "main" and app.root:
            app.root.iconify()
            logger.info("主窗口已最小化")
        elif window_name in app.popup_windows:
            popup = app.popup_windows[window_name]
            if popup and popup.winfo_exists():
                popup.iconify()
                logger.info(f"弹出窗口已最小化: {window_name}")
            else:
                logger.warning(f"弹出窗口不存在或已销毁: {window_name}")
        else:
            logger.warning(f"窗口不存在: {window_name}")
    except Exception as e:
        logger.error(f"最小化窗口失败: {window_name} - {e}")


@registry.register("window-hide")
def cmd_window_hide(app, window_name: str):
    """隐藏指定窗口"""
    try:
        if window_name == "main" and app.root:
            app.root.withdraw()
            logger.info("主窗口已隐藏")
        elif window_name in app.popup_windows:
            popup = app.popup_windows[window_name]
            if popup and popup.winfo_exists():
                popup.withdraw()
                logger.info(f"弹出窗口已隐藏: {window_name}")
            else:
                logger.warning(f"弹出窗口不存在或已销毁: {window_name}")
        else:
            logger.warning(f"窗口不存在: {window_name}")
    except Exception as e:
        logger.error(f"隐藏窗口失败: {window_name} - {e}")


@registry.register("window-show")
def cmd_window_show(app, window_name: str):
    """显示指定窗口"""
    try:
        if window_name == "main" and app.root:
            app.root.deiconify()
            logger.info("主窗口已显示")
        elif window_name in app.popup_windows:
            popup = app.popup_windows[window_name]
            if popup and popup.winfo_exists():
                popup.deiconify()
                logger.info(f"弹出窗口已显示: {window_name}")
            else:
                logger.warning(f"弹出窗口不存在或已销毁: {window_name}")
        else:
            logger.warning(f"窗口不存在: {window_name}")
    except Exception as e:
        logger.error(f"显示窗口失败: {window_name} - {e}")


@registry.register("show")
def cmd_show(app):
    """显示所有已建立的GUI元件（最終指令）"""
    try:
        # 確保主窗口可見
        if app.root:
            app.root.deiconify()
            logger.info("GUI界面已显示")
        else:
            logger.warning("主窗口未创建，无法显示GUI")
    except Exception as e:
        logger.error(f"显示GUI失败: {e}")


@registry.register("emoji-picker")
def cmd_emoji_picker(app, name: str, x: str, y: str, width: str, height: str, *props):
    """創建表情符號選擇器"""
    try:
        params = parse_parameters(list(props))

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过表情符号选择器创建")
            return

        # 創建表情符號選擇器
        from .ui_components import create_emoji_picker
        emoji_picker = create_emoji_picker(
            app.root, name, int(x), int(y), int(width), int(height), **params
        )

        # 存儲引用
        if not hasattr(app, 'emoji_pickers'):
            app.emoji_pickers = {}
        app.emoji_pickers[name] = emoji_picker

        logger.debug(f"創建表情符號選擇器: {name}")

    except Exception as e:
        logger.error(f"創建表情符號選擇器失敗: {name} - {e}")


@registry.register("emoji-show")
def cmd_emoji_show(app, emoji_picker_name: str, target: str, *props):
    """顯示選擇的表情符號"""
    try:
        if not hasattr(app, 'emoji_pickers') or emoji_picker_name not in app.emoji_pickers:
            logger.warning(f"表情符號選擇器不存在: {emoji_picker_name}")
            return

        emoji_picker = app.emoji_pickers[emoji_picker_name]
        selected_emoji = emoji_picker.get_selected_emoji()

        if not selected_emoji:
            app.show_message("提示", "請先選擇表情符號")
            return

        # 更新目標控件
        if '.' in target:
            widget_name, attr = target.split('.', 1)
            widget = app.controls.get(widget_name)
            if widget:
                if attr == 'text' and hasattr(widget, 'config'):
                    widget.config(text=selected_emoji)
                elif attr == 'value' and hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                    widget.delete(0, 'end')
                    widget.insert(0, selected_emoji)
        else:
            # 直接在控件上顯示
            widget = app.controls.get(target)
            if widget and hasattr(widget, 'config'):
                widget.config(text=selected_emoji)

        logger.debug(f"顯示表情符號: {selected_emoji} -> {target}")

    except Exception as e:
        logger.error(f"顯示表情符號失敗: {e}")


@registry.register("emoji-set")
def cmd_emoji_set(app, emoji: str, target: str):
    """直接設置表情符號到目標控件"""
    try:
        # 更新目標控件
        if '.' in target:
            widget_name, attr = target.split('.', 1)
            widget = app.controls.get(widget_name)
            if widget:
                if attr == 'text' and hasattr(widget, 'config'):
                    widget.config(text=emoji)
                elif attr == 'value' and hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                    widget.delete(0, 'end')
                    widget.insert(0, emoji)
        else:
            # 直接在控件上顯示
            widget = app.controls.get(target)
            if widget and hasattr(widget, 'config'):
                widget.config(text=emoji)

        logger.debug(f"設置表情符號: {emoji} -> {target}")

    except Exception as e:
        logger.error(f"設置表情符號失敗: {e}")


@registry.register("show_window_info")
def cmd_show_window_info(app):
    """顯示當前窗口資訊"""
    try:
        if not app.root:
            logger.warning("主窗口不存在")
            return

        # 獲取窗口尺寸
        width = app.root.winfo_width()
        height = app.root.winfo_height()
        x = app.root.winfo_x()
        y = app.root.winfo_y()

        # 創建資訊字符串
        info = f"窗口位置: ({x}, {y})\n窗口尺寸: {width} x {height}"

        # 更新狀態標籤
        status_label = app.controls.get('statusLabel')
        if status_label:
            status_label.config(text=f"當前窗口大小: {width}x{height}")

        # 顯示詳細資訊
        app.show_message("窗口資訊", info)
        logger.info(f"窗口資訊: 位置({x},{y}), 尺寸({width}x{height})")

    except Exception as e:
        logger.error(f"顯示窗口資訊失敗: {e}")
        app.show_message("錯誤", f"獲取窗口資訊失敗: {e}")


@registry.register("workspace")
def cmd_workspace(app, name: str, *args):
    """創建工作區（有邊框的容器區域）"""
    try:
        # 解析所有參數
        all_args = [name] + list(args)
        params = parse_parameters(all_args)

        # 检查GUI是否可用
        if not app.root:
            logger.warning("GUI环境不可用，跳过工作区创建")
            return

        # 创建工作区框架
        workspace_frame = tk.Frame(
            app.root,
            relief=tk.SOLID,  # 實心邊框
            borderwidth=2,    # 邊框寬度
            bg=params.get("bg", "#f8f8f8")  # 背景色
        )

        # 檢查是否使用相對定位
        if "relx" in params or "rely" in params or "relwidth" in params or "relheight" in params:
            # 相對定位
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
            else:
                place_args["anchor"] = "nw"

            workspace_frame.place(**place_args)

            # 存儲自適應配置以供後續調整
            workspace_frame._responsive_config = {
                "relx": float(params.get("relx", 0)),
                "rely": float(params.get("rely", 0)),
                "relwidth": float(params.get("relwidth", 1)),
                "relheight": float(params.get("relheight", 1)),
                "anchor": params.get("anchor", "nw")
            }
        else:
            # 絕對定位 - 使用原始參數
            x = params.get("x", "0")
            y = params.get("y", "0")
            width = params.get("w", "200")
            height = params.get("h", "150")

            workspace_frame.place(
                x=int(x),
                y=int(y),
                width=int(width),
                height=int(height)
            )

        # 存储工作区引用
        if not hasattr(app, 'workspaces'):
            app.workspaces = {}
        app.workspaces[name] = workspace_frame

        logger.debug(f"創建工作區: {name}")

    except Exception as e:
        logger.error(f"創建工作區失敗: {name} - {e}")


@registry.register("workspace-add")
def cmd_workspace_add(app, workspace_name: str, ctrl_type: str, ctrl_name: str, *args):
    """在工作區中添加控件"""
    try:
        if not hasattr(app, 'workspaces') or workspace_name not in app.workspaces:
            logger.warning(f"工作區不存在: {workspace_name}")
            return

        workspace_frame = app.workspaces[workspace_name]

        # 解析所有參數
        all_args = [workspace_name, ctrl_type, ctrl_name] + list(args)
        params = parse_parameters(all_args)

        # 解析位置和尺寸（相對於工作區）
        x = int(params.get("x", 0))
        y = int(params.get("y", 0))
        w = int(params.get("w", 0)) if "w" in params else None
        h = int(params.get("h", 0)) if "h" in params else None

        # 获取样式
        cls = params.get("class")
        style = app.styles.get(cls, {}) if cls else {}

        # 创建控件
        widget = _create_widget(workspace_frame, ctrl_type, params, style)

        # 设置位置（相對於工作區）
        if w and h:
            widget.place(x=x, y=y, width=w, height=h)
        else:
            widget.place(x=x, y=y)

        # 存储控件引用
        app.controls[ctrl_name] = widget

        logger.debug(f"在工作區 {workspace_name} 中添加控件: {ctrl_name}")

    except Exception as e:
        logger.error(f"在工作區中添加控件失敗: {ctrl_name} - {e}")


@registry.register("show_message")
def cmd_show_message(app, title: str = "訊息", message: str = "這是一個測試訊息"):
    """顯示訊息對話框"""
    try:
        app.show_message(title, message)
        logger.debug(f"顯示訊息: {title} - {message}")
    except Exception as e:
        logger.error(f"顯示訊息失敗: {e}")


@registry.register("get")
def cmd_get(app, target: str, *properties):
    """統一的狀態查詢指令 - 取得各種組件或系統的狀態信息"""
    try:
        result = {}

        # 解析目標對象
        target_type, target_name = _parse_target(target)

        # 根據目標類型和屬性獲取信息
        if target_type == "window":
            result = _get_window_info(app, target_name, properties)
        elif target_type == "control":
            result = _get_control_info(app, target_name, properties)
        elif target_type == "workspace":
            result = _get_workspace_info(app, target_name, properties)
        elif target_type == "popup":
            result = _get_popup_info(app, target_name, properties)
        elif target_type == "emoji":
            result = _get_emoji_info(app, target_name, properties)
        elif target_type == "system":
            result = _get_system_info(app, properties)
        else:
            logger.warning(f"未知的查詢目標: {target}")
            return

        # 格式化並顯示結果
        if result:
            _display_get_result(app, target, properties, result)
        else:
            logger.info(f"查詢 {target} 無結果")

        logger.debug(f"取得指令執行: {target} {properties}")

    except Exception as e:
        logger.error(f"取得指令執行失敗: {target} - {e}")


def _parse_target(target: str) -> Tuple[str, Optional[str]]:
    """解析目標對象，返回 (類型, 名稱)"""
    if target == "system":
        return "system", None
    elif target == "emoji":
        return "emoji", None
    elif target.startswith("window"):
        if target == "window":
            return "window", "main"
        else:
            # window:main, window:popup1 等
            parts = target.split(":", 1)
            return "window", parts[1] if len(parts) > 1 else "main"
    elif target.startswith("control:"):
        parts = target.split(":", 1)
        return "control", parts[1] if len(parts) > 1 else None
    elif target.startswith("workspace:"):
        parts = target.split(":", 1)
        return "workspace", parts[1] if len(parts) > 1 else None
    elif target.startswith("popup:"):
        parts = target.split(":", 1)
        return "popup", parts[1] if len(parts) > 1 else None
    else:
        # 默認嘗試作為控件名
        return "control", target


def _get_window_info(app, window_name: str, properties):
    """獲取窗口信息"""
    result = {}

    if window_name == "main" and app.root:
        window = app.root
    elif hasattr(app, 'popup_windows') and window_name in app.popup_windows:
        window = app.popup_windows[window_name]
    else:
        return result

    if not window or not window.winfo_exists():
        return result

    for prop in properties:
        if prop in ["position", "pos", "位置"]:
            result["position"] = f"({window.winfo_x()}, {window.winfo_y()})"
        elif prop in ["size", "尺寸"]:
            result["size"] = f"{window.winfo_width()}x{window.winfo_height()}"
        elif prop in ["title", "標題"]:
            result["title"] = window.title()
        elif prop in ["visible", "可見"]:
            result["visible"] = "是" if window.winfo_viewable() else "否"
        elif prop in ["state", "狀態"]:
            try:
                state = window.state()
                result["state"] = state
            except:
                result["state"] = "normal"

    return result


def _get_control_info(app, control_name: str, properties):
    """獲取控件信息"""
    result = {}

    widget = app.controls.get(control_name)
    if not widget or not widget.winfo_exists():
        return result

    for prop in properties:
        if prop in ["text", "文字"]:
            if hasattr(widget, 'cget'):
                text = widget.cget('text')
                result["text"] = text if text else ""
            elif hasattr(widget, 'get'):
                try:
                    text = widget.get()
                    result["text"] = text if text else ""
                except:
                    result["text"] = ""
        elif prop in ["position", "pos", "位置"]:
            try:
                info = widget.place_info()
                x = info.get('x', '0')
                y = info.get('y', '0')
                result["position"] = f"({x}, {y})"
            except:
                result["position"] = "(0, 0)"
        elif prop in ["size", "尺寸"]:
            try:
                width = widget.winfo_width()
                height = widget.winfo_height()
                result["size"] = f"{width}x{height}"
            except:
                result["size"] = "0x0"
        elif prop in ["font", "字形"]:
            try:
                font = widget.cget('font')
                if isinstance(font, tuple):
                    result["font"] = f"{font[0]}, {font[1]}"
                else:
                    result["font"] = str(font)
            except:
                result["font"] = "default"
        elif prop in ["color", "顏色"]:
            try:
                fg = widget.cget('fg') or widget.cget('foreground')
                bg = widget.cget('bg') or widget.cget('background')
                result["color"] = f"前景: {fg}, 背景: {bg}"
            except:
                result["color"] = "default"
        elif prop in ["type", "類型"]:
            if isinstance(widget, tk.Button):
                result["type"] = "button"
            elif isinstance(widget, tk.Label):
                result["type"] = "label"
            elif isinstance(widget, tk.Entry):
                result["type"] = "entry"
            else:
                result["type"] = "unknown"
        elif prop in ["state", "狀態"]:
            try:
                state = widget.cget('state')
                result["state"] = state if state else "normal"
            except:
                result["state"] = "normal"

    return result


def _get_workspace_info(app, workspace_name: str, properties):
    """獲取工作區信息"""
    result = {}

    if not hasattr(app, 'workspaces') or workspace_name not in app.workspaces:
        return result

    workspace = app.workspaces[workspace_name]
    if not workspace or not workspace.winfo_exists():
        return result

    for prop in properties:
        if prop in ["position", "pos", "位置"]:
            try:
                info = workspace.place_info()
                if 'relx' in info:
                    result["position"] = f"相對位置 (relx: {info.get('relx')}, rely: {info.get('rely')})"
                else:
                    x = info.get('x', '0')
                    y = info.get('y', '0')
                    result["position"] = f"絕對位置 ({x}, {y})"
            except:
                result["position"] = "未知"
        elif prop in ["size", "尺寸"]:
            try:
                width = workspace.winfo_width()
                height = workspace.winfo_height()
                result["size"] = f"{width}x{height}"
            except:
                result["size"] = "0x0"
        elif prop in ["color", "顏色"]:
            try:
                bg = workspace.cget('bg')
                result["color"] = f"背景: {bg}"
            except:
                result["color"] = "default"

    return result


def _get_popup_info(app, popup_name: str, properties):
    """獲取彈出窗口信息"""
    result = {}

    if not hasattr(app, 'popup_windows') or popup_name not in app.popup_windows:
        return result

    popup = app.popup_windows[popup_name]
    if not popup or not popup.winfo_exists():
        return result

    # 與窗口信息獲取相同
    return _get_window_info(app, popup_name, properties)


def _get_emoji_info(app, emoji_name: str, properties):
    """獲取表情符號信息"""
    result = {}

    if hasattr(app, 'emoji_pickers') and emoji_name in app.emoji_pickers:
        picker = app.emoji_pickers[emoji_name]
        for prop in properties:
            if prop in ["selected", "選擇"]:
                selected = picker.get_selected_emoji()
                result["selected"] = selected if selected else "無"
            elif prop in ["count", "數量"]:
                result["count"] = str(len(picker.get_all_emojis()))
    else:
        # 全局表情符號狀態
        for prop in properties:
            if prop in ["available", "可用"]:
                result["available"] = "表情符號選擇器已載入"
            elif prop in ["status", "狀態"]:
                result["status"] = "就緒"

    return result


def _get_system_info(app, properties):
    """獲取系統信息"""
    result = {}

    for prop in properties:
        if prop in ["time", "時間"]:
            from datetime import datetime
            result["time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif prop in ["controls", "控件"]:
            result["controls"] = str(len(app.controls)) if hasattr(app, 'controls') else "0"
        elif prop in ["workspaces", "工作區"]:
            result["workspaces"] = str(len(app.workspaces)) if hasattr(app, 'workspaces') else "0"
        elif prop in ["popups", "彈出窗口"]:
            result["popups"] = str(len(app.popup_windows)) if hasattr(app, 'popup_windows') else "0"
        elif prop in ["version", "版本"]:
            result["version"] = "MENU002 v2.1.0"
        elif prop in ["memory", "記憶體"]:
            import psutil
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                result["memory"] = f"{memory_mb:.1f} MB"
            except:
                result["memory"] = "無法獲取"

    return result


def _display_get_result(app, target: str, properties, result: Dict[str, str]):
    """顯示查詢結果"""
    if not result:
        message = f"查詢 {target} 無可用信息"
    else:
        lines = [f"📋 查詢結果 - {target}:"]
        for key, value in result.items():
            lines.append(f"  {key}: {value}")
        message = "\n".join(lines)

    # 顯示在狀態欄（如果有）
    if hasattr(app, 'status_bar'):
        app.status_bar.set_status(f"查詢完成: {target}")

    # 顯示訊息對話框或記錄到日誌
    if app.root:
        app.show_message("查詢結果", message)
    else:
        logger.info(message)