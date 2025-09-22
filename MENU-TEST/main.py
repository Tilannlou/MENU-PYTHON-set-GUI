#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MENU002 优化版主入口文件
提供系统启动和配置功能
"""

import sys
import os
import argparse
import json
import traceback
from pathlib import Path
from typing import Optional, Dict, Any

# 添加当前目录到Python路径
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

try:
    from utils.logger import logger, configure_logging, LOG_LEVELS
    from utils.constants import CONFIG_FILES
    from core import MenuApp, registry
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有必要模块已正确安装")
    sys.exit(1)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="MENU002 优化版 GUI 指令系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用范例:
  python main.py examples/demo.menu              # 基本使用
  python main.py -d examples/demo.menu           # 调试模式
  python main.py -l DEBUG examples/demo.menu     # 详细日志
  python main.py --config custom_config.json     # 自定义配置
        """
    )

    parser.add_argument(
        "script",
        nargs="?",
        help="MENU脚本文件路径"
    )

    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="启用调试模式"
    )

    parser.add_argument(
        "-l", "--log-level",
        choices=list(LOG_LEVELS.keys()),
        default="INFO",
        help="设置日志级别 (默认: INFO)"
    )

    parser.add_argument(
        "-c", "--config",
        help="指定配置文件路径"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="MENU002 优化版 v2.0.0"
    )

    return parser.parse_args()


def find_default_script() -> Optional[Path]:
    """查找默认脚本文件"""
    default_paths = [
        current_dir / "examples" / "demo.menu",
        current_dir / "examples" / "simple_demo.menu",
        current_dir / "demo.menu"
    ]
    
    for path in default_paths:
        if path.exists():
            return path
    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """加载配置文件"""
    default_config = {
        "debug": False,
        "log_level": "INFO",
        "window": {
            "default_size": "800x600",
            "default_title": "MENU002 应用"
        },
        "api": {
            "timeout": 30,
            "connection_timeout": 10
        },
        "ui": {
            "show_toolbar": True,
            "show_statusbar": True,
            "theme": "default"
        }
    }

    # 尝试加载默认配置文件
    if not config_path:
        config_file = current_dir / CONFIG_FILES['DEFAULT_CONFIG']
        if config_file.exists():
            config_path = str(config_file)

    if not config_path or not os.path.exists(config_path):
        logger.warning("未找到配置文件，使用默认配置")
        return default_config

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info(f"加载配置文件: {config_path}")
            
            # 合并配置，确保所有必要的键都存在
            return {**default_config, **config}
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return default_config


def initialize_system(config: Dict[str, Any]) -> bool:
    """初始化系统"""
    try:
        # 设置日志级别
        log_level = config.get('log_level', 'INFO')
        configure_logging(log_level)

        # 设置调试模式
        if config.get('debug', False):
            logger.info("调试模式已启用")
            _register_debug_commands()

        # 初始化插件系统
        _initialize_plugin_system()

        logger.info("系统初始化完成")
        return True

    except Exception as e:
        logger.error(f"系统初始化失败: {e}")
        return False


def _register_debug_commands():
    """注册调试指令"""
    try:
        @registry.register("debug-info")
        def cmd_debug_info(app, *args):
            """显示调试信息"""
            info = f"""
调试信息:
- 控件数量: {len(app.controls) if hasattr(app, 'controls') else 'N/A'}
- 样式数量: {len(app.styles) if hasattr(app, 'styles') else 'N/A'}
- 显示区域数量: {len(app.display_areas) if hasattr(app, 'display_areas') else 'N/A'}
- 弹出窗口数量: {len(app.popup_windows) if hasattr(app, 'popup_windows') else 'N/A'}
- 当前语言: {app.language.get_current_language() if hasattr(app, 'language') else 'N/A'}
            """.strip()
            app.show_message("调试信息", info)

        @registry.register("debug-controls")
        def cmd_debug_controls(app, *args):
            """列出所有控件"""
            if not hasattr(app, 'controls') or not app.controls:
                app.show_message("控件列表", "没有创建任何控件")
                return

            controls_info = "控件列表:\n" + "\n".join(
                f"- {name}: {type(widget).__name__}"
                for name, widget in app.controls.items()
            )
            app.show_message("控件列表", controls_info)

        @registry.register("debug-memory")
        def cmd_debug_memory(app, *args):
            """显示内存使用信息"""
            try:
                import psutil
                process = psutil.Process(os.getpid())
                memory_info = process.memory_info()

                info = f"""
内存使用信息:
- RSS (物理内存): {memory_info.rss / 1024 / 1024:.1f} MB
- VMS (虚拟内存): {memory_info.vms / 1024 / 1024:.1f} MB
                """.strip()

                app.show_message("内存信息", info)

            except ImportError:
                app.show_message("内存信息", "psutil 模块未安装，无法获取详细内存信息")

        logger.debug("调试指令注册完成")

    except Exception as e:
        logger.error(f"调试指令注册失败: {e}")


def _initialize_plugin_system():
    """初始化插件系统"""
    try:
        # 检查插件配置文件是否存在
        plugin_config = current_dir / CONFIG_FILES['PLUGIN_CONFIG']
        if not plugin_config.exists():
            logger.debug("插件配置文件不存在，跳过插件系统初始化")
            return

        # 尝试加载插件系统
        from core.plugin_system import PluginManager, PluginCommandBus

        logger.info("初始化插件系统...")
        plugin_manager = PluginManager(str(plugin_config))
        command_bus = PluginCommandBus(registry)
        plugin_manager.command_bus = command_bus

        # 初始化所有插件
        plugin_manager.initialize_plugins()
        plugin_info = plugin_manager.get_plugin_info()
        logger.info(f"插件系统初始化完成: {plugin_info}")

    except ImportError as e:
        logger.debug(f"插件系统模块不存在: {e}")
    except Exception as e:
        logger.error(f"插件系统初始化失败: {e}")


def setup_exception_handling():
    """设置全局异常处理"""
    def exception_handler(exc_type, exc_value, exc_traceback):
        """全局异常处理器"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 用户中断
            logger.info("用户中断程序")
            return

        # 记录异常详细信息
        logger.critical(
            "未捕获的异常",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

        # 在GUI环境中显示错误对话框
        try:
            import tkinter as tk
            from tkinter import messagebox

            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            error_msg = f"程序遇到未预期的错误:\n{str(exc_value)}\n\n请查看日志文件以获取详细信息。"
            messagebox.showerror("严重错误", error_msg)
            root.destroy()

        except ImportError:
            # 非GUI环境
            print(f"严重错误: {exc_value}", file=sys.stderr)
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)

    # 设置异常处理器
    sys.excepthook = exception_handler


def validate_script_path(script_path: str) -> Optional[Path]:
    """验证脚本路径并返回绝对路径"""
    if not script_path:
        return None
        
    script_path_obj = Path(script_path)
    if not script_path_obj.is_absolute():
        script_path_obj = current_dir / script_path_obj
        
    if not script_path_obj.exists():
        logger.error(f"脚本文件不存在: {script_path_obj}")
        return None
        
    return script_path_obj


def main():
    """主函数"""
    try:
        # 设置异常处理
        setup_exception_handling()

        # 解析命令行参数
        args = parse_arguments()

        # 加载配置
        config = load_config(args.config)
        
        # 覆盖命令行参数中的设置
        if args.debug:
            config['debug'] = True
        if args.log_level:
            config['log_level'] = args.log_level

        # 初始化系统
        if not initialize_system(config):
            logger.error("系统初始化失败")
            return 1

        # 处理脚本路径
        script_path = validate_script_path(args.script)
        if not script_path:
            # 尝试查找默认脚本
            script_path = find_default_script()
            if not script_path:
                logger.error("未提供脚本文件且未找到默认脚本")
                return 1
            logger.info(f"使用默认脚本: {script_path}")

        # 创建应用
        logger.info(f"加载MENU脚本: {script_path}")
        app = MenuApp(str(script_path))

        # 构建UI
        app.build_ui()

        # 运行应用
        logger.info("MENU002 应用启动成功!")
        app.run()

        return 0

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.critical(f"程序执行失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())