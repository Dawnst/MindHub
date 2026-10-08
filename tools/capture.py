#!/usr/bin/env python3
"""
工作台主页 · 实景截图脚本
前提：一个跑着**虚构演示数据**的工作台实例（默认 8392，见 make_demo_data.py 与 README 重截步骤）。
用法：python3 tools/capture.py [BASE]   （在仓库根目录执行；输出到 assets/）
说明：纯客户端 WB.showPage() 切页后截视口，不产生任何数据写入。
"""
from playwright.sync_api import sync_playwright
import pathlib
import sys

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8392"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"
PAGES = [
    ("overview", "shot-overview"),
    ("life",     "shot-life"),
    ("goal",     "shot-goal"),
    ("project",  "shot-project"),
    ("action",   "shot-action"),
    ("focus",    "shot-focus"),
    ("stat",     "shot-stat"),
]

def main():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE, wait_until="networkidle")
        pg.wait_for_timeout(1600)
        pg.evaluate("document.documentElement.setAttribute('data-theme','light')")
        pg.wait_for_timeout(300)
        for pid, name in PAGES:
            pg.evaluate(f"WB.showPage('{pid}')")
            pg.wait_for_timeout(1100)
            pg.screenshot(path=str(OUT / f"{name}.png"))
            print("ok", name)
        # 暗色总览（Hero 亮暗双版用）
        pg.evaluate("WB.showPage('overview')")
        pg.evaluate("document.documentElement.setAttribute('data-theme','dark')")
        pg.wait_for_timeout(700)
        pg.screenshot(path=str(OUT / "shot-overview-dark.png"))
        print("ok overview-dark")
        b.close()
        print("pageerrors:", errs if errs else "none")

if __name__ == "__main__":
    main()
