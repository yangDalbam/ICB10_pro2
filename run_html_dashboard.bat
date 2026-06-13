@echo off
chcp 65001 > nul
title Korea Trip Data랩 - HTML 대시보드 실행기
echo ===================================================
echo  Korea Trip Data랩 - 정적 HTML 대시보드 실행기
echo ===================================================
echo.
echo [정보] 브라우저 보안 정책(file:// 제한)을 우회하기 위해
echo        로컬 웹 서버(http://localhost:8000)를 구동합니다.
echo.
echo [안내] 자동으로 브라우저가 열리지 않으면 아래 주소로 접속해 주세요:
echo        👉 http://localhost:8000/korea_trip_dashboard.html
echo.
echo ※ 대시보드 사용을 마치시면 이 창을 닫아주세요.
echo ===================================================
echo.

:: 기본 웹브라우저로 대시보드 주소 오픈
start http://localhost:8000/korea_trip_dashboard.html

:: 가상환경 파이썬을 이용해 dist 디렉토리를 루트로 하는 로컬 웹 서버 실행
.venv\Scripts\python -m http.server 8000 --directory korea-trip-data/dist
