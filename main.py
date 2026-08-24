"""游戏入口：python main.py 启动图形界面，加 --sim 运行 AI 自检对战。"""

from __future__ import annotations

import sys


def main() -> int:
    if "--sim" in sys.argv:
        from aethercall.simulate import main as sim_main
        return sim_main()
    try:
        from aethercall.ui import main as ui_main
    except ImportError:
        print("未找到 tkinter，请安装带 Tk 支持的 Python（Windows 官方安装包默认自带）。")
        return 1
    ui_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
