@echo off
echo ==========================================
echo Nancy Four-Brain Architecture Benchmark
echo ==========================================

echo Checking Nancy services...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Nancy services...
    docker-compose up -d
    timeout /t 30 >nul
)

echo Running benchmark...
python automated_benchmark.py --run

echo Benchmark completed!
pause