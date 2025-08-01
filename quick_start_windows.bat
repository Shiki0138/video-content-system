@echo off
REM VideoAI Studio クイックスタート for Windows

echo ======================================
echo   VideoAI Studio を起動します
echo ======================================
echo.

REM 仮想環境がなければ作成
if not exist "venv" (
    echo 初回セットアップ中...
    python -m venv venv
)

REM 仮想環境をアクティベート
call venv\Scripts\activate

REM 必要なパッケージをインストール（初回のみ）
if not exist "venv\.installed" (
    echo 必要なパッケージをインストール中...
    pip install --upgrade pip
    pip install -r requirements.txt
    echo. > venv\.installed
    echo インストール完了
)

REM Webアプリを起動
echo.
echo Webアプリを起動中...
echo ブラウザで http://localhost:8003 を開いてください
echo.
echo 終了するには Ctrl+C を押してください
echo.
python web_app.py