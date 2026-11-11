"""Start the Chladni Visualizer web app on http://127.0.0.1:8102 (local only).

Run: python run_web.py [--port 8102]
Needs: pip install -r requirements-web.txt
"""
import argparse

import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8102)
    port = ap.parse_args().port
    print(f"Chladni Visualizer web app: http://127.0.0.1:{port}")
    uvicorn.run("web.app:app", host="127.0.0.1", port=port)
