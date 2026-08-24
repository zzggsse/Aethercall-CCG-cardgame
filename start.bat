@echo off
chcp 65001 >nul
title 灵契战歌 · Aethercall
cd /d "%~dp0"

echo ============================================
echo    灵契战歌 Aethercall - 正在启动...
echo ============================================
echo.

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)

if not defined PY (
    echo [错误] 未检测到 Python。
    echo 请先安装 Python 3.10 或更高版本: https://www.python.org/downloads/
    echo 安装时请勾选 "Add python.exe to PATH"。
    echo.
    pause
    exit /b 1
)

%PY% -c "import tkinter" >nul 2>nul
if errorlevel 1 (
    echo [错误] 当前 Python 缺少 tkinter 图形库，无法启动界面。
    echo 建议改用 python.org 官方安装包安装 Python。
    echo.
    pause
    exit /b 1
)

%PY% main.py
if errorlevel 1 (
    echo.
    echo [提示] 程序异常退出，请将以上信息反馈。
    pause
)
exit /b 0