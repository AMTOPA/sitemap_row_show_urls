@echo off
chcp 65001 >nul
title Sitemap URL提取工具

:: 检查Python是否可用
where python >nul 2>&1 || (
    echo 错误：未找到Python，请先安装Python并添加到PATH
    pause
    exit /b 1
)


:: 正常执行


python main.py 

echo.
pause