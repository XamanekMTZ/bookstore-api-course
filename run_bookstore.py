#!/usr/bin/env python3
"""
Скрипт для запуска BookStore API
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Запуск BookStore API...")
    print("📚 Документация: http://localhost:8000/docs")
    print("🔍 ReDoc: http://localhost:8000/redoc")
    print("❤️ Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "bookstore.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )