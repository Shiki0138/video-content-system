#!/usr/bin/env python3
"""
シンプルなプレビューサーバー
"""

import http.server
import socketserver
import webbrowser

PORT = 8000

print("🚀 シンプルプレビューサーバー起動中...")
print(f"📍 URL: http://localhost:{PORT}")
print("🛑 終了: Ctrl+C")
print("\n📁 以下のファイルが閲覧可能です:")
print("  - output/ : 生成された出力ファイル")
print("  - _posts/ : Jekyll記事")
print("  - *.png : サムネイル画像")

# ブラウザを開く
webbrowser.open(f"http://localhost:{PORT}")

# サーバー起動
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 サーバーを停止しました")