import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
from app import create_app

app = create_app()

if __name__ == "__main__":
    # 優先讀取 CLI 傳入的 port，否則使用環境變數，再來 fallback 為 80
    port = 80
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    else:
        port = int(os.environ.get("PORT", 80))

    app.run(host="0.0.0.0", port=port, debug=True)
