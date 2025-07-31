#!/usr/bin/env python3
"""
生成されたコンテンツをプレビューする簡易サーバー
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# 生成されたファイルを表示するHTMLページ
def create_preview_html():
    posts_dir = Path("_posts")
    output_dir = Path("output")
    
    # 最新の投稿を取得
    posts = sorted(posts_dir.glob("*.md"), reverse=True) if posts_dir.exists() else []
    
    # 最新の出力ディレクトリを取得
    outputs = sorted(output_dir.glob("*"), reverse=True) if output_dir.exists() else []
    
    html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Content System - Preview</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: #1a1a2e;
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #1a1a2e;
            margin-top: 0;
        }
        .file-list {
            list-style: none;
            padding: 0;
        }
        .file-list li {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        .file-list a {
            color: #3b82f6;
            text-decoration: none;
        }
        .file-list a:hover {
            text-decoration: underline;
        }
        .thumbnail {
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }
        pre {
            background: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎬 Video Content System - Preview</h1>
        <p>生成されたコンテンツのプレビュー</p>
    </div>
    """
    
    # 最新の出力を表示
    if outputs:
        latest_output = outputs[0]
        html += f"""
    <div class="container">
        <div class="card">
            <h2>📁 最新の出力: {latest_output.name}</h2>
            <ul class="file-list">
        """
        
        # 各ファイルをリスト
        for file in latest_output.glob("*"):
            if file.is_file():
                rel_path = file.relative_to(Path.cwd())
                html += f'<li><a href="{rel_path}" target="_blank">{file.name}</a></li>\n'
        
        html += """
            </ul>
        </div>
        """
        
        # サムネイルを表示
        thumbnail = latest_output / "thumbnail.png"
        if thumbnail.exists():
            html += f"""
        <div class="card">
            <h2>🎨 サムネイル</h2>
            <img src="{thumbnail.relative_to(Path.cwd())}" class="thumbnail" alt="Thumbnail">
        </div>
            """
        
        # YouTube説明文を表示
        youtube = latest_output / "youtube_description.txt"
        if youtube.exists():
            content = youtube.read_text(encoding='utf-8')[:500] + "..."
            html += f"""
        <div class="card">
            <h2>📺 YouTube説明文</h2>
            <pre>{content}</pre>
        </div>
            """
        
        # X投稿文を表示
        twitter = latest_output / "twitter_post.txt"
        if twitter.exists():
            content = twitter.read_text(encoding='utf-8')
            html += f"""
        <div class="card">
            <h2>🐦 X投稿文</h2>
            <pre>{content}</pre>
        </div>
            """
    
    html += """
    </div>
    
    <div class="container" style="margin-top: 30px;">
        <div class="card" style="grid-column: 1 / -1;">
            <h2>📝 Jekyll記事一覧</h2>
            <ul class="file-list">
    """
    
    # Jekyll記事をリスト
    for post in posts[:10]:  # 最新10件
        html += f'<li><a href="{post.relative_to(Path.cwd())}" target="_blank">{post.name}</a></li>\n'
    
    html += """
            </ul>
        </div>
    </div>
</body>
</html>
    """
    
    # index.htmlとして保存
    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(html)

# HTTPサーバーを起動
class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    PORT = 8000
    
    # プレビューHTML生成
    create_preview_html()
    
    # サーバー起動
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 プレビューサーバー起動")
        print(f"📍 URL: http://localhost:{PORT}/preview.html")
        print(f"🛑 終了: Ctrl+C")
        
        # ブラウザを開く
        webbrowser.open(f"http://localhost:{PORT}/preview.html")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 サーバーを停止しました")

if __name__ == "__main__":
    main()