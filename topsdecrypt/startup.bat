@echo off
chcp 936 >nul <nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
title PyCrypt 加密 / 解密

rem ============================================================
rem  PyCrypt 启动脚本
rem    1. 选择 加密 / 解密
rem    2. 逐项配置参数：直接回车 = 用默认值，输入内容 = 用输入的内容
rem    3. 用 python x.py 的方式执行 encrypt.py / decrypt.py
rem
rem  注意：本文件必须存成 GBK(cp936) + CRLF，否则 cmd 解析会错位。
rem ============================================================

rem ---------- 默认参数（要改默认值就改这里）----------
rem 加密（encrypt.py）
set "DEF_ENC_INPUT=E:\vba\perf-xxxt\perf-xxxt\decrypt\encrypt"
set "DEF_ENC_OUTPUT=E:\vba\perf-xxxt\perf-xxxt\decrypt\decrypt"
set "DEF_ENC_EXCLUDE=.cache,.tmp"
set "DEF_ENC_SUFFIX=.topsdecrypt"
set "DEF_ENC_KEEP=True"
rem 解密（decrypt.py）
set "DEF_DEC_TARGET=E:\vba\perf-xxxt\perf-xxxt\decrypt\decrypt"
set "DEF_DEC_STRIP=.topsdecrypt"
set "DEF_DEC_RECURSIVE=True"
set "DEF_DEC_CONFLICT=overwrite"

where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 没有找到 python 命令，请先安装 Python 并把 python.exe 加入 PATH。
    echo.
    pause
    goto :end
)

:menu
cls
echo ============================================================
echo             PyCrypt 文件加密 / 解密工具
echo ============================================================
echo.
echo    [1] 加密    生成「原文件名 + 目标后缀」的新文件
echo    [2] 解密    去掉文件的目标后缀
echo    [0] 退出
echo.
set "MODE="
set /p "MODE=请输入序号后回车（直接回车 = 1 加密）："
if not defined MODE set "MODE=1"
if "%MODE%"=="1" goto :do_encrypt
if "%MODE%"=="2" goto :do_decrypt
if "%MODE%"=="0" goto :end
echo.
echo [提示] 序号无效，请重新输入。
pause
goto :menu


rem ============================================================
rem  加密
rem ============================================================
:do_encrypt
echo.
echo ---------- 配置【加密】参数（直接回车 = 使用默认值）----------
echo   说明：输入 - 表示留空；路径末尾的反斜杠会自动去掉
echo.
call :ask "输入路径（要遍历的源文件夹）      " "%DEF_ENC_INPUT%"   INPUT_DIR
call :ask "输出路径（新文件存放的文件夹）    " "%DEF_ENC_OUTPUT%"  OUTPUT_DIR
call :ask "排除的后缀（逗号分隔，- 为留空）  " "%DEF_ENC_EXCLUDE%" EXCLUDE_S
call :ask "目标后缀（新文件名加的后缀）      " "%DEF_ENC_SUFFIX%"  TARGET_SUFFIX
call :ask "保留原目录结构（True/False）      " "%DEF_ENC_KEEP%"    KEEP_STRUCT
call :trimbs INPUT_DIR
call :trimbs OUTPUT_DIR

echo.
echo ============================================================
echo   命令：python encrypt.py
echo   输入路径     ：%INPUT_DIR%
echo   输出路径     ：%OUTPUT_DIR%
echo   排除后缀     ：%EXCLUDE_S%
echo   目标后缀     ：%TARGET_SUFFIX%
echo   保留目录结构 ：%KEEP_STRUCT%
echo ============================================================
echo.
echo 按任意键开始执行，按 Ctrl+C 取消...
pause >nul
echo.
python encrypt.py "%INPUT_DIR%" "%OUTPUT_DIR%" "%EXCLUDE_S%" "%TARGET_SUFFIX%" "%KEEP_STRUCT%"
echo.
echo [退出码] !errorlevel!
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu


rem ============================================================
rem  解密
rem ============================================================
:do_decrypt
echo.
echo ---------- 配置【解密】参数（直接回车 = 使用默认值）----------
echo   说明：路径末尾的反斜杠会自动去掉
echo.
call :ask "目标目录（要去后缀的文件夹）      " "%DEF_DEC_TARGET%"    TARGET_DIR
call :ask "要去掉的后缀（如 .bak）           " "%DEF_DEC_STRIP%"     SUFFIX_STRIP
call :ask "递归遍历子目录（True/False）      " "%DEF_DEC_RECURSIVE%" RECURSIVE
call :ask "重名处理（overwrite/skip/rename） " "%DEF_DEC_CONFLICT%"  ON_CONFLICT
call :trimbs TARGET_DIR

echo.
echo ============================================================
echo   命令：python decrypt.py
echo   目标目录     ：%TARGET_DIR%
echo   去掉后缀     ：%SUFFIX_STRIP%
echo   递归子目录   ：%RECURSIVE%
echo   重名处理     ：%ON_CONFLICT%
echo ============================================================
echo.
echo 按任意键开始执行，按 Ctrl+C 取消...
pause >nul
echo.
python decrypt.py "%TARGET_DIR%" "%SUFFIX_STRIP%" "%RECURSIVE%" "%ON_CONFLICT%"
echo.
echo [退出码] !errorlevel!
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu


rem ============================================================
rem  子程序：提示用户输入，回车则保留默认值
rem    %1 = 提示文字   %2 = 默认值   %3 = 存放结果的变量名
rem ============================================================
:ask
set "%~3=%~2"
set "_IN="
set /p "_IN=%~1[默认: %~2] : "
if defined _IN set "%~3=%_IN%"
if "!%~3!"=="-" set "%~3="
goto :eof


rem ============================================================
rem  子程序：去掉变量值末尾的反斜杠
rem    （否则 "%PATH%" 会变成 "...\" 结尾，传参时 \" 会被当成转义）
rem    %1 = 变量名
rem ============================================================
:trimbs
set "_TB=!%~1!"
:trimbs_loop
set "_LAST=!_TB:~-1!"
if not "!_LAST!"=="\" goto :trimbs_done
set "_TB=!_TB:~0,-1!"
goto :trimbs_loop
:trimbs_done
set "%~1=!_TB!"
goto :eof


:end
endlocal
exit /b 0
