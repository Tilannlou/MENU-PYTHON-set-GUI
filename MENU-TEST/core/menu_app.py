"""
主应用类模块
提供MENU002系统的核心应用逻辑
"""

import shlex
import os
import subprocess
from typing import Any, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import messagebox

from utils.logger import logger
from utils.helpers import parse_command_line, generate_unique_id
from utils.constants import COMMAND_ALIASES, PROCESSING_ORDER
from .command_registry import registry
from .language_manager import LanguageManager
from .api_manager import api_manager
from .ui_components import DisplayArea, CodeDisplayArea


class MenuApp:
    """
    MENU002 主应用类
    负责脚本解析、UI构建和事件处理
    """

    def __init__(self, script_path: str):
        """
        初始化应用

        Args:
            script_path: 脚本文件路径
        """
        self.script_path = script_path
        self.controls: Dict[str, tk.Widget] = {}
        self.styles: Dict[str, Dict[str, str]] = {}
        self.exec_map: Dict[str, List[str]] = {}
        self.binding_list: List[Tuple[str, str, str]] = []
        self.root: Optional[tk.Tk] = None
        self.grid_cfg: Optional[Dict[str, Any]] = None
        self.display_areas: Dict[str, DisplayArea] = {}
        self.language = LanguageManager()
        self.show_code_comparison = False
        self.cmds = self.load_script()

        # 弹出窗口管理
        self.popup_windows: Dict[str, tk.Toplevel] = {}

        # 插件系统支持
        self.command_bus = None

        logger.info(f"初始化MENU002应用: {script_path}")

    def load_script(self) -> List[List[str]]:
        """
        加载脚本文件

        Returns:
            解析后的指令列表
        """
        cmds = []
        try:
            with open(self.script_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or not line.startswith(("menu ", "#")):
                        continue

                    # 跳过注释
                    if line.startswith("#"):
                        continue

                    try:
                        # 解析命令行
                        toks = parse_command_line(line)  # parse_command_line 已經處理了 'menu' 前綴
                        if not toks:
                            continue

                        # 支持指令别名
                        cmd = toks[0].lower()
                        if cmd in COMMAND_ALIASES:
                            cmd = COMMAND_ALIASES[cmd]
                            toks = [cmd] + toks[1:]

                        # 跳过 'show' 指令（稍后处理）
                        if cmd == "show":
                            break

                        cmds.append(toks)

                    except Exception as e:
                        logger.warning(f"解析脚本第 {line_num} 行失败: {e}")
                        # 继续处理下一行，不中断整个脚本

        except FileNotFoundError:
            logger.error(f"脚本文件不存在: {self.script_path}")
            raise
        except Exception as e:
            logger.error(f"加载脚本失败: {e}")
            raise

        logger.info(f"加载脚本完成: {len(cmds)} 条指令")
        return cmds

    def build_ui(self):
        """
        构建用户界面
        按照正确的顺序处理所有指令
        """
        try:
            logger.info("开始构建UI")

            # 1. 处理基本指令（窗口、样式、控件等）
            self._process_basic_commands()

            # 2. 处理插件指令
            self._process_plugin_commands()

            # 3. 处理弹出窗口指令
            self._process_popup_commands()

            # 4. 绑定执行行为
            self._bind_exec_actions()

            # 5. 绑定事件
            self._bind_events()

            # 6. 显示代码对照（如果启用）
            if self.show_code_comparison:
                self.generate_code_view()

            logger.info("UI构建完成")

        except Exception as e:
            logger.error(f"UI构建失败: {e}")
            # 不抛出异常，继续运行应用

    def _process_basic_commands(self):
        """处理基本指令"""
        for toks in self.cmds:
            cmd = toks[0].lower()

            # 跳过弹出窗口相关指令
            if cmd in ['popup-window', 'popup-content', 'popup-send-data']:
                continue

            handler = registry.get(cmd)
            if handler:
                try:
                    handler(self, *toks[1:])
                except Exception as e:
                    logger.error(f"执行指令 {cmd} 时出错: {e}")
                    # 继续处理其他指令，不中断整个过程

    def _process_plugin_commands(self):
        """处理插件指令"""
        if hasattr(self, 'command_bus'):
            for toks in self.cmds:
                cmd = toks[0].lower()
                if hasattr(self.command_bus, 'command_mapper') and cmd in self.command_bus.command_mapper:
                    try:
                        self.command_bus.execute_command(cmd, self, *toks[1:])
                    except Exception as e:
                        logger.error(f"执行插件指令 {cmd} 时出错: {e}")
                        # 继续处理其他指令，不中断整个过程

    def _process_popup_commands(self):
        """处理弹出窗口指令"""
        # 分组处理不同类型的弹出窗口指令
        popup_commands = {
            'popup-window': [],
            'popup-content': [],
            'popup-send-data': []
        }

        for toks in self.cmds:
            cmd = toks[0].lower()
            if cmd in popup_commands:
                popup_commands[cmd].append(toks)

        # 按照正确顺序执行
        for cmd_toks in popup_commands['popup-window']:
            try:
                registry.get('popup-window')(self, *cmd_toks[1:])
            except Exception as e:
                logger.error(f"执行popup-window指令时出错: {e}")
                # 继续处理其他指令，不中断整个过程

        for cmd_toks in popup_commands['popup-content']:
            try:
                registry.get('popup-content')(self, *cmd_toks[1:])
            except Exception as e:
                logger.error(f"执行popup-content指令时出错: {e}")
                # 继续处理其他指令，不中断整个过程

        for cmd_toks in popup_commands['popup-send-data']:
            try:
                registry.get('popup-send-data')(self, *cmd_toks[1:])
            except Exception as e:
                logger.error(f"执行popup-send-data指令时出错: {e}")
                # 继续处理其他指令，不中断整个过程

    def _bind_exec_actions(self):
        """绑定执行行为"""
        for btn_name, templates in self.exec_map.items():
            widget = self.controls.get(btn_name)
            if not widget:
                logger.warning(f"找不到控件进行执行绑定: {btn_name}")
                continue

            cb = self.make_exec_cb(templates)

            # 按钮使用 config，其他控件使用 bind
            if isinstance(widget, tk.Button):
                widget.config(command=cb)
            else:
                widget.bind("<Button-1>", lambda e, fn=cb: fn())

    def _bind_events(self):
        """绑定事件"""
        for name, event, action in self.binding_list:
            widget = self.controls.get(name)
            if not widget:
                logger.warning(f"找不到控件进行事件绑定: {name}")
                continue

            # 事件映射
            evt_map = {
                "click": "<Button-1>",
                "doubleclick": "<Double-Button-1>",
                "keyrelease": "<KeyRelease>"
            }

            evt = evt_map.get(event.lower(), f"<{event}>")
            widget.bind(evt, lambda e, act=action: self.handle_binding(act))

    def make_exec_cb(self, templates: List[str]) -> callable:
        """
        创建执行回调

        Args:
            templates: 命令模板列表

        Returns:
            回调函数
        """
        def on_click():
            try:
                # 准备上下文
                ctx = {n: w.get() for n, w in self.controls.items()
                       if hasattr(w, "get")}

                for tpl in templates:
                    try:
                        cmd = format_string_with_context(tpl, ctx)
                        proc = subprocess.run(cmd, shell=True,
                                              capture_output=True, text=True)
                        messagebox.showinfo("执行结果", proc.stdout or proc.stderr)
                    except Exception as ex:
                        messagebox.showerror("错误", str(ex))

            except Exception as e:
                messagebox.showerror("错误", str(e))

        return on_click

    def handle_binding(self, action: str):
        """
        处理绑定事件

        Args:
            action: 动作字符串
        """
        try:
            action = action.strip()

            # 支持函数调用格式，如 "send_message()" 或 "update_status()"
            if action.endswith("()"):
                # 处理函数调用
                func_name = action[:-2]  # 移除末尾的"()"

                # 检查是否是内建方法
                if hasattr(self, func_name):
                    func = getattr(self, func_name)
                    if callable(func):
                        func()  # 调用方法
                        logger.debug(f"绑定函数调用: {action}")
                        return

                # 检查是否是注册的指令处理器
                handler = registry.get(func_name.lower())
                if handler:
                    handler(self)
                    logger.debug(f"绑定指令调用: {action}")
                    return

                logger.warning(f"绑定函数不存在: {func_name}")
                return

            # 支持直接指令调用，如 "show_window_info"
            if action and not "=" in action:
                # 检查是否是注册的指令处理器
                handler = registry.get(action.lower())
                if handler:
                    handler(self)
                    logger.debug(f"绑定指令调用: {action}")
                    return

                logger.warning(f"绑定指令不存在: {action}")
                return

            # 处理「target.attr = expr」格式的赋值
            if "=" in action:
                parts = action.split("=", 1)
                lhs = parts[0].strip()
                rhs = parts[1].strip()

                if "." in lhs:
                    target, attr = lhs.split(".", 1)
                    target = target.strip()
                    attr = attr.strip()
                else:
                    # 如果没有点，则假设是全局变量更新
                    target = lhs
                    attr = "value"

                # 准备上下文
                ctx = {}
                for name, widget in self.controls.items():
                    if hasattr(widget, 'get') and callable(getattr(widget, 'get')):
                        try:
                            ctx[name] = widget.get()
                        except:
                            ctx[name] = str(widget)
                    else:
                        ctx[name] = widget

                # 添加应用实例到上下文
                ctx['self'] = self
                ctx['app'] = self

                val = safe_eval_expression(rhs, ctx)
                widget = self.controls.get(target)

                if not widget:
                    logger.warning(f"绑定目标控件不存在: {target}")
                    return

                # 更新控件属性
                if attr == "text" and hasattr(widget, "config"):
                    widget.config(text=str(val))
                elif attr == "value" and hasattr(widget, "delete") and hasattr(widget, "insert"):
                    widget.delete(0, "end")
                    widget.insert(0, str(val))
                elif attr == "content" and hasattr(widget, "delete") and hasattr(widget, "insert"):
                    widget.config(state="normal")
                    widget.delete(1.0, "end")
                    widget.insert("end", str(val))
                    widget.config(state="disabled")
                else:
                    # 尝试设置属性
                    try:
                        setattr(widget, attr, val)
                    except AttributeError:
                        logger.warning(f"控件 {target} 没有属性 {attr}")

                logger.debug(f"绑定更新: {target}.{attr} = {val}")
            else:
                logger.warning(f"不支持的绑定格式: {action}")

        except Exception as ex:
            logger.error(f"绑定处理失败: {action} - {ex}")
            # 不显示错误对话框，因为这会影响用户体验

    def generate_code_view(self):
        """生成并显示代码对照视图"""
        if not self.root:
            logger.warning("主窗口不存在，无法生成代码视图")
            return

        try:
            # 创建代码对照窗口
            code_window = tk.Toplevel(self.root)
            code_window.title("代码对照")
            code_window.geometry("800x600")

            # 创建文本框
            code_text = tk.Text(code_window, wrap=tk.WORD)
            code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 生成代码
            code_lines = self._generate_python_code()
            code_text.insert(tk.END, "\n".join(code_lines))
            code_text.config(state=tk.DISABLED)

            logger.debug("代码对照视图已生成")

        except Exception as e:
            logger.error(f"代码视图生成失败: {e}")

    def _generate_python_code(self) -> List[str]:
        """生成Python代码"""
        code_lines = ["# MENU002 生成的代码"]
        code_lines.append("import tkinter as tk")
        code_lines.append("")
        code_lines.append("class GeneratedApp:")
        code_lines.append("    def __init__(self):")
        code_lines.append("        self.root = tk.Tk()")

        if self.root:
            code_lines.append(f"        self.root.title('{self.root.title()}')")
            code_lines.append(f"        self.root.geometry('{self.root.winfo_width()}x{self.root.winfo_height()}')")
        else:
            code_lines.append("        self.root.title('Generated App')")
            code_lines.append("        self.root.geometry('800x600')")

        code_lines.append("        self.controls = {}")
        code_lines.append("")

        # 添加控件创建代码
        for name, widget in self.controls.items():
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

    def run(self):
        """运行应用"""
        if self.root:
            logger.info("MENU002 应用启动")
            self.root.mainloop()
        else:
            logger.error("主窗口未创建，无法运行应用")

    def get_control(self, name: str) -> Optional[tk.Widget]:
        """
        获取控件

        Args:
            name: 控件名称

        Returns:
            控件对象或None
        """
        control = self.controls.get(name)
        if not control:
            logger.warning(f"控件不存在: {name}")
        return control

    def get_display_area(self, name: str) -> Optional[DisplayArea]:
        """
        获取显示区域

        Args:
            name: 显示区域名称

        Returns:
            显示区域对象或None
        """
        area = self.display_areas.get(name)
        if not area:
            logger.warning(f"显示区域不存在: {name}")
        return area

    def set_status(self, message: str, status_type: str = 'info'):
        """
        设置状态信息

        Args:
            message: 状态消息
            status_type: 状态类型
        """
        if hasattr(self, 'status_bar'):
            self.status_bar.set_status(message, status_type)

    def show_message(self, title: str, message: str, message_type: str = 'info'):
        """
        显示消息框

        Args:
            title: 消息框标题
            message: 消息内容
            message_type: 消息类型 (info, warning, error)
        """
        if message_type == 'error':
            messagebox.showerror(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)

    # 其他方法保持不变...


# 导入必要的函数
from utils.helpers import format_string_with_context, safe_eval_expression
from datetime import datetime