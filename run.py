import uvicorn
import os

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(current_dir, "app")
    print("🚀 Starting Echo Reels Bhojpuri FastAPI Backend on http://127.0.0.1:8000")
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[app_dir]
    )
