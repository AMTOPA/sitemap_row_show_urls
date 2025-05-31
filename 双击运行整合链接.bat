@echo off
chcp 65001 >nul
title Sitemap URL提取工具

:: 检查Python是否可用
where python >nul 2>&1 || (
    echo 错误：未找到Python，请先安装Python并添加到PATH
    pause
    exit /b 1
)

:: 首次运行处理
if not exist mywebsite.txt (
    python main.py
    if errorlevel 1 (
        echo 首次配置失败，请检查错误信息
    ) else (
        echo 首次配置已完成
    )
    pause
    exit /b
)

:: 正常执行
echo 正在提取URL，请稍候...
python main.py > log.txt 2>&1

:: 结果处理
if errorlevel 1 (
    echo.
    type log.txt
    echo.
    echo ❌ 操作失败
) else (
    :: 统计URL数量
    setlocal enabledelayedexpansion
    set count=0
    if exist urls.txt (
        for /f "delims=" %%a in (urls.txt) do (
            set /a count+=1
        )
    )
    
    echo.
    echo ✅ 操作成功，共提取 !count! 个URL
    
    :: 显示URL逻辑
    if !count! gtr 20 (
        echo 前20个URL：
        set n=0
        for /f "delims=" %%a in (urls.txt) do (
            echo %%a
            set /a n+=1
            if !n! equ 20 goto :break
        )
        :break
        echo.
        echo 完整列表请查看urls.txt文件
    ) else (
        echo 全部URL列表：
        type urls.txt
    )
    endlocal
)

echo.
pause