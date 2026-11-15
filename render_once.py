"""GitHub Actions 单次渲染入口: 起 Flask → 渲染 → 存 dashboard.png (带一次重试)"""
import threading
import time
import sys

from app import app
from config import Config


def _serve():
    # 开发服务器线程: 仅监听本地, 供 Playwright 抓取 /dashboard
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def _render_once():
    from renderer import render_dashboard_to_bytes
    bio = render_dashboard_to_bytes("http://127.0.0.1:5000/dashboard")
    with open("dashboard.png", "wb") as f:
        f.write(bio.getvalue())
    print("dashboard.png saved")


def main():
    t = threading.Thread(target=_serve, daemon=True)
    t.start()
    time.sleep(5)

    attempts = 2
    for i in range(1, attempts + 1):
        try:
            _render_once()
            print(f"render OK (attempt {i})")
            return
        except Exception as e:
            print(f"render attempt {i} failed: {e}")
            if i < attempts:
                time.sleep(10)
    sys.exit(1)


if __name__ == "__main__":
    main()
