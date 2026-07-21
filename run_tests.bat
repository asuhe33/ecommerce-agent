@echo off
chcp 65001 >nul
echo ========================================
echo   电商 Agent — 自动化测试
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 运行单元测试（无需外部服务）...
echo.
pytest tests/ -v -m "not integration" --tb=short
echo.

echo [2/2] 运行集成测试（需要 MySQL + Ollama）...
echo.
pytest tests/test_integration.py -v --tb=short
echo.
echo ========================================
echo   测试完成
echo ========================================
pause
