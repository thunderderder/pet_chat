import subprocess
import time
import requests
import os
import signal
import sys

def log(msg):
    print(msg)
    with open("verify_log.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def verify():
    log("Starting server...")
    # 启动 server，使用 new environment 避免环境变量干扰，但要保留 PATH
    env = os.environ.copy()
    env["VERIFY_SSL"] = "False"
    
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # 等待启动
        log("Waiting for server to start...")
        for i in range(10):
            try:
                requests.get("http://127.0.0.1:8000/")
                log("Server is up!")
                break
            except:
                time.sleep(1)
        else:
            log("Server failed to start within 10 seconds.")
            out, err = proc.communicate(timeout=1)
            log(f"Stdout: {out.decode()}")
            log(f"Stderr: {err.decode()}")
            return

        # 测试 API
        log("Testing /api/analyze...")
        if not os.path.exists('test.png'):
             log("Error: test.png not found")
             return

        files = {'file': ('test.png', open('test.png', 'rb'), 'image/png')}
        try:
            resp = requests.post("http://127.0.0.1:8000/api/analyze", files=files, timeout=35) # 给足够的时间等待外部API超时
            log(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                log(f"Response: {resp.json()}")
                log("✅ MVP verification successful!")
            else:
                log(f"❌ API returned error: {resp.text}")
        except Exception as e:
            log(f"❌ Request failed: {e}")

    finally:
        log("Stopping server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()
        log("Server stopped.")

if __name__ == "__main__":
    verify()
