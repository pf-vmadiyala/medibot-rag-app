@echo off
echo 🚀 Starting MediBot RAG App services...

:: 1. Start Backend API in a new window
echo 🔌 Starting FastAPI Backend on http://localhost:8000...
start "MediBot Backend API" uv run uvicorn api:app --port 8000

:: 2. Wait 2 seconds for backend initialization
timeout /t 2 /nobreak >nul

:: 3. Start Next.js Frontend in a new window
echo 💻 Starting Next.js Frontend on http://localhost:3001...
cd frontend
start "MediBot Next.js Frontend" npm run dev -- -p 3001
cd ..

echo.
echo ✅ Both services have been launched in separate terminal windows!
echo 💡 To stop the services, simply close those terminal windows.
pause
