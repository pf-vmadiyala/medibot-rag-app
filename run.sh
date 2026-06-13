#!/bin/bash

# Terminate all spawned background jobs when this script exits or is interrupted
trap 'kill 0' EXIT

echo "🚀 Starting MediBot RAG App services..."

# 1. Start Backend API
echo "🔌 Starting FastAPI Backend on http://localhost:8000..."
uv run uvicorn api:app --port 8000 &
BACKEND_PID=$!

# 2. Wait 2 seconds for backend initialization
sleep 2

# 3. Start Next.js Frontend
echo "💻 Starting Next.js Frontend on http://localhost:3001..."
cd frontend
npm run dev -- -p 3001 &
FRONTEND_PID=$!

# Keep script running and wait for background jobs
wait
